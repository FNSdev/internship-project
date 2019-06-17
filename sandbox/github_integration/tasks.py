from __future__ import absolute_import, unicode_literals
from celery import shared_task
from github_integration.utils.repository import get_repository_info, get_repository_branches, get_repository_tree
from github_integration.utils.utils import parse_tree
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
                    url = '/'.join((repository.url, 'tree', name))
                    branch = Branch(
                        name=name,
                        url=url,
                        repository=repository,
                        commit_sha=br.get('commit').get('sha')
                    )
                    branch.save()

                    error, data = get_repository_tree(
                        user.github_token,
                        user.github_username,
                        repository_name,
                        branch.commit_sha
                    )
                    if error is None:
                        tree = data.get('tree')
                        parse_tree(tree, branch=branch)
                        repository.status = Repository.UPDATED
                        repository.save()
                    else:
                        error_message = f'An error occurred when getting branch {name} content : {error}'
            else:
                error_message = f'An error occurred when getting {repository_name} branches : {error}'
    else:
        error_message = f'An error occurred when getting {repository_name} details : {error}'

    if error_message is not None and repository is not None:
        repository.delete()

    return error_message


@shared_task
def update_repository_task(user_email, repository_id):
    repository = Repository.objects.get(id=repository_id)

    if repository.status == repository.UPDATE_IN_PROGRESS:
        return f'{repository.name} update was in progress already'

    repository.status = Repository.UPDATE_IN_PROGRESS
    repository.save()

    user = User.objects.get(email=user_email)
    error_message = None

    error, _ = get_repository_info(user.github_token, user.github_username, repository.name)
    if error is None:
        error, branches = get_repository_branches(user.github_token, user.github_username, repository.name)
        if error is None:
            for branch in branches:
                existing_branch = Branch.objects.get(name=branch.get('name'))
                if existing_branch.commit_sha != branch.get('commit').get('sha'):
                    new_branch = Branch(
                        name=existing_branch.name,
                        url=existing_branch.url,
                        repository=repository,
                        commit_sha=branch.get('commit').get('sha')
                    )
                    new_branch.save()

                    error, data = get_repository_tree(
                        user.github_token,
                        user.github_username,
                        repository.name,
                        branch.get('commit').get('sha')
                    )
                    if error is None:
                        tree = data.get('tree')
                        parse_tree(tree, branch=new_branch)
                        existing_branch.delete()
                    else:
                        error_message = f'An error occurred when getting branch {new_branch.name} content : {error}'
        else:
            error_message = f'An error occurred when getting {repository.name} branches'
    elif error == Errors.NOT_FOUND:
        error_message = f'Repository {repository.name} was not found. Was it deleted from github?'
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
            update_repository_task.delay(user.email, repository.id)
