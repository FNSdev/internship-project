from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.db import transaction
from github_integration.github_client_api.exceptions import GitHubApiRequestException, GitHubApiNotFound
from github_integration.github_client_api.github_client import GitHubClient
from github_integration.models import Repository, Branch
from user.models import User
from core.models import Project


@shared_task
def create_repository_task(user_email, repository_name):
    """Creates new repository"""

    user = User.objects.get(email=user_email)
    client = GitHubClient(user.github_token)
    try:
        # Get repository info
        repo = client.get_repository_info(user.github_username, repository_name)

        # If repository was already added, return
        if Repository.objects.filter(id=repo['id']).exists():
            # TODO write to log
            return f'{repository_name} already exists'

        repository = Repository(
            id=repo['id'],
            name=repo['name'],
            url=repo['html_url'],
            status=Repository.UPDATE_IN_PROGRESS,
            user=user
        )
        repository.save()

        with transaction.atomic():
            # Get repository branches
            branches = client.get_repository_branches(user.github_username, repository_name)
            for br in branches:
                name = br.get('name')
                _ = Branch.objects.create_branch_with_content(
                    user=user,
                    name=br['name'],
                    url='/'.join((repository.url, 'tree', name)),
                    repository=repository,
                    commit_sha=br['commit']['sha'],
                )

        repository.status = Repository.UPDATED
        repository.save()

    except GitHubApiRequestException as e:
        # TODO write to log
        print('Request Exception')
        # logger.log(e.message + repository.name)
        raise GitHubApiRequestException


@shared_task(ignore_result=True)
def update_repository_task(user_email, repository_id):
    """Updates content of existing repository"""

    repository = Repository.objects.get(id=repository_id)

    # Check if repository update is not in progress already and
    # if repository was deleted from GitHub
    # TODO write to log
    if repository.status == repository.UPDATE_IN_PROGRESS:
        return f'{repository.name} update was in progress already'
    elif repository.status == repository.DELETED_ON_GITHUB:
        return f'{repository.name} was deleted from GitHub'

    repository.status = Repository.UPDATE_IN_PROGRESS
    repository.save()

    user = User.objects.get(email=user_email)
    client = GitHubClient(user.github_token)

    with transaction.atomic():
        try:
            # Check if repository still exists. If not, change it status to DELETED_ON_GITHUB
            _ = client.get_repository_info(user.github_username, repository.name)
        except GitHubApiNotFound:
            # TODO write to log
            repository.status = repository.DELETED_ON_GITHUB
            repository.save()

        try:
            branches = client.get_repository_branches(user.github_username, repository.name)
            current_branches_set = set(repository.branches.all())
            actual_branches_set = set()

            for branch in branches:
                commit_sha = branch['commit']['sha']
                try:
                    # If branch is not new, check if we need to update branch by comparing last commit's sha
                    existing_branch = repository.branches.get(name=branch.get('name'))
                    if existing_branch.commit_sha != commit_sha:
                        print(f'need to update branch {existing_branch.name}')
                        new_branch = Branch.objects.create_branch_with_content(
                            client,
                            user.github_username,
                            existing_branch.name,
                            existing_branch.url,
                            repository,
                            commit_sha
                        )
                        actual_branches_set.add(new_branch)
                    else:
                        actual_branches_set.add(existing_branch)
                except Branch.DoesNotExist:
                    # If branch is new, create new Branch object
                    new_branch = Branch.objects.create_branch_with_content(
                        client,
                        user.github_username,
                        branch.get('name'),
                        '/'.join((repository.url, 'tree', branch.get('name'))),
                        repository,
                        commit_sha
                    )
                    actual_branches_set.add(new_branch)

            # If everything is OK, delete obsolete branches
            branches_to_remove = current_branches_set.difference(actual_branches_set)
            for branch in branches_to_remove:
                branch.delete()

            try:
                # If this repository has project with auto-sync option, update it's tasks
                project = repository.project
                if project.auto_sync_with_github:
                    for task in project.tasks.all():
                        branches = repository.branches.filter(name__icontains=f'task_{task.task_id}/')
                        task.branches.add(*branches)
                        task.save()
            except Project.DoesNotExist:
                pass

        except GitHubApiRequestException as e:
            # TODO write to log
            print(e.message)
            raise GitHubApiRequestException

    # Save repository
    repository.status = Repository.UPDATED
    repository.save()


@shared_task(ignore_result=True)
def update_repositories_task():
    """Updates all saved repositories"""

    users = User.objects.all()
    for user in users:
        repositories = user.repositories.all()
        for repository in repositories:
            update_repository_task.delay(user.email, repository.id).forget()
