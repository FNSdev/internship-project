from django import views
from django.shortcuts import reverse, render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from core.models import Project
from github_integration.github_client_api.github_client import GitHubClient
from github_integration.github_client_api.exceptions import GitHubApiRequestException
from github_integration.github_client_api.parsers import parse_path
from github_integration.tasks import create_repository_task
from github_integration.models import Repository
from celery.result import AsyncResult


class AddRepositoryView(LoginRequiredMixin, views.View):
    def post(self, request):
        repository_name = request.POST.get('repository')
        task = create_repository_task.delay(request.user.email, repository_name)
        return JsonResponse({'message': 'Task in queue', 'task_id': task.id})


class GetCeleryTaskStatusView(LoginRequiredMixin, views.View):
    """Checks if celery task with specific id is ready"""

    def get(self, request):
        task_id = request.GET.get('task_id')
        task = AsyncResult(task_id)
        if task.ready():
            message = task.get()
            if message is None:
                message = 'Success!'
            return JsonResponse({'status': 'ready', 'message': message})
        return JsonResponse({'status': 'not-ready'})


class GetGithubTokenView(LoginRequiredMixin, views.View):
    """Listens to GitHub login callback"""

    def get(self, request):
        code = request.GET['code']
        client = GitHubClient(None)
        try:
            # Sending code back to GitHub in order to get OAuth token
            token = client.create_token(code)['access_token']
            client._token = token

            # Getting GitHub username
            username = client.get_username()['login']

            # Updating user info
            user = request.user
            user.github_username = username
            user.github_token = token
            user.save()

            messages.info(request, 'Github token and username were added successfully')
            # TODO write to log
        except GitHubApiRequestException:
            messages.warning(request, 'Request Exception')

        return HttpResponseRedirect(reverse('user:profile'))


class CreateGithubTokenView(LoginRequiredMixin, views.View):
    """Redirects to GitHub"""

    def get(self, request):
        return HttpResponseRedirect(GitHubClient.get_github_login_url())


class GetRepositoryTreeView(views.View):
    """Returns saved repository structure as json"""

    def get(self, request, **kwargs):
        repository = get_object_or_404(Repository, id=kwargs['id'])
        return JsonResponse(repository.get_repository_tree())


class GithubRepositoriesView(LoginRequiredMixin, views.View):
    """Lists all GitHub repositories, that user owns"""

    def get(self, request):
        user = request.user
        client = GitHubClient(user.github_token)
        try:
            repos = client.get_repository_list()
            repositories = []
            for repo in repos:
                repositories.append({
                    'name': repo.get('name'),
                    'url': repo.get('html_url'),
                    'description': repo.get('description'),
                    'id': repo.get('id')
                })

            ctx = {
                'repositories': repositories
            }
            return render(request, 'github_integration/remote_repositories.html', context=ctx)
            # TODO write to log
        except GitHubApiRequestException:
            messages.warning(request, 'Request Exception')


class RepositoriesView(LoginRequiredMixin, views.View):
    """Lists all repositories, that user has saved"""

    def get(self, request):
        repositories = request.user.repositories.all()

        ctx = {
            'repositories': repositories
        }
        return render(request, 'github_integration/repositories.html', context=ctx)


class RepositoryView(LoginRequiredMixin, views.View):
    def get(self, request, **kwargs):
        repository = get_object_or_404(Repository, id=kwargs['id'])
        if repository.user != request.user:
            try:
                project = repository.project
                if not project.team.filter(email=request.user.email):
                    raise PermissionDenied('You can not access this repository')
            except Project.DoesNotExist:
                raise PermissionDenied('You can not access this repository')

        ctx = {
            'branches': repository.branches.all()
        }
        return render(request, 'github_integration/repository.html', context=ctx)


class BranchView(LoginRequiredMixin, views.View):
    """
    Lists branch content.
    If content is a directory, user can open it and see all inner content.
    If content is a file, request is made to get this file's text
    """

    def get(self, request, **kwargs):
        repository = get_object_or_404(Repository, id=kwargs['id'])
        if repository.user != request.user:
            try:
                project = repository.project
                if not project.team.filter(email=request.user.email):
                    raise PermissionDenied('You can not access this repository')
            except Project.DoesNotExist:
                raise PermissionDenied('You can not access this repository')

        branch = repository.branches.get(repository=repository, commit_sha=kwargs['commit_sha'])

        path = kwargs.get('path')
        content_type, data = parse_path(
            repository.user.github_token,
            path,
            branch
        )

        ctx = {
            'data': data,
            'type': content_type,
        }
        return render(request, 'github_integration/branch.html', context=ctx)
