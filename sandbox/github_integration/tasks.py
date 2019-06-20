from __future__ import absolute_import, unicode_literals
from celery import shared_task
from github_integration.utils.repository import get_repository_info, get_repository_branches, get_repository_tree
from github_integration.utils.utils import create_branch, parse_tree
from github_integration.utils.decorators import Errors
from github_integration.models import Repository, Branch
from user.models import User


@shared_task
def create_repository_task(user_email, repository_name):
    user = User.objects.get(email=user_email)
    repository = None
    error_message = None

    error, repo = get_repository_info(user.github_token, user.github_username, repository_name)
    if error is None:
        try:
            Repository.objects.get(id=repo.get('id'))
            error_message = f'Repository {repository_name} already exists'
            return error_message
        except Repository.DoesNotExist:
            repository = Repository(
                id=repo.get('id'),
                name=repo.get('name'),
                url=repo.get('html_url'),
                status=Repository.UPDATE_IN_PROGRESS,
                user=user
            )
            repository.save()

            error, branches = get_repository_branches(user.github_token, user.github_username, repository_name)
            if error is None:
                for br in branches:
                    name = br.get('name')
                    branch = create_branch(
                        user,
                        br.get('name'),
                        '/'.join((repository.url, 'tree', name)),
                        repository,
                        br.get('commit').get('sha')
                    )
                    if branch is None:
                        error_message = f'An error occurred when getting branch {name} content : {error}'
                        break
            else:
                error_message = f'An error occurred when getting {repository_name} branches : {error}'
    else:
        error_message = f'An error occurred when getting {repository_name} details : {error}'

    if error_message is not None and repository is not None:
        repository.delete()
    else:
        repository.status = Repository.UPDATED
        repository.save()

    return error_message


@shared_task
def update_repository_task(user_email, repository_id):
    repository = Repository.objects.get(id=repository_id)

    if repository.status == repository.UPDATE_IN_PROGRESS:
        return f'{repository.name} update was in progress already'
    elif repository.status == repository.DELETED_ON_GITHUB:
        return f'{repository.name} was deleted from GitHub'

    repository.status = Repository.UPDATE_IN_PROGRESS
    repository.save()

    user = User.objects.get(email=user_email)
    error_message = None

    error, _ = get_repository_info(user.github_token, user.github_username, repository.name)
    if error is None:
        error, branches = get_repository_branches(user.github_token, user.github_username, repository.name)
        if error is None:
            current_branches_set = set(repository.branches.all())
            actual_branches_set = set()
            for branch in branches:
                commit_sha = branch.get('commit').get('sha')
                try:
                    existing_branch = repository.branches.get(name=branch.get('name'))
                    if existing_branch.commit_sha != commit_sha:
                        print(f'need to update branch {existing_branch.name}')
                        new_branch = create_branch(
                            user,
                            existing_branch.name,
                            existing_branch.url,
                            repository,
                            commit_sha
                        )
                        if new_branch is None:
                            error_message = f'An error occurred when getting branch {new_branch.name} content : {error}'
                            break
                        else:
                            actual_branches_set.add(new_branch)
                    else:
                        actual_branches_set.add(existing_branch)
                except Branch.DoesNotExist:
                    new_branch = create_branch(
                        user,
                        branch.get('name'),
                        '/'.join((repository.url, 'tree', branch.get('name'))),
                        repository,
                        commit_sha
                    )
                    if new_branch is None:
                        error_message = f'An error occurred when getting branch {new_branch.name} content : {error}'
                    else:
                        actual_branches_set.add(new_branch)
            if error_message is None:
                branches_to_remove = current_branches_set.difference(actual_branches_set)
                for branch in branches_to_remove:
                    branch.delete()
        else:
            error_message = f'An error occurred when getting {repository.name} branches'
    elif error == Errors.NOT_FOUND:
        error_message = f'Repository {repository.name} was not found. Was it deleted from github?'
        repository.status = Repository.DELETED_ON_GITHUB
        repository.save()
        return error_message
    else:
        error_message = f'An error occurred when updating {repository.name} details : {error}'

    repository.status = Repository.UPDATED
    repository.save()

    return error_message


@shared_task
def update_repositories_task():
    users = User.objects.all()
    for user in users:
        repositories = user.repositories.all()
        for repository in repositories:
            update_repository_task.delay(user.email, repository.id).forget()
