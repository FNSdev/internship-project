import base64
from django import views
from django.shortcuts import reverse, render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from github_integration.utils.token import get_login_url, create_token, get_username
from github_integration.utils.repository import get_repository_list, get_blob
from github_integration.tasks import create_repository_task
from github_integration.models import Repository, Content
from celery.result import AsyncResult


class AddRepositoryView(LoginRequiredMixin, views.View):
    def post(self, request):
        repository_name = request.POST.get('repository')
        task = create_repository_task.delay(request.user.email, repository_name)
        return JsonResponse({'message': 'Task in queue', 'task_id': task.id})


class GetTaskStatusView(LoginRequiredMixin, views.View):
    def get(self, request):
        task_id = request.GET.get('task_id')
        task = AsyncResult(task_id)
        if task.ready():
            message = task.get()
            if message is None:
                message = 'Success!'
            print(message)
            return JsonResponse({'status': 'ready', 'message': message})
        return JsonResponse({'status': 'not-ready'})


class GetGithubTokenView(LoginRequiredMixin, views.View):
    def get(self, request):
        code = request.GET.get('code')

        error, token = create_token(code)
        if error is None:
            error, username = get_username(token)
            if error is None:
                messages.add_message(request, messages.INFO, 'Github token and username were added successfully')
                user = request.user
                user.github_username = username
                user.github_token = token
                user.save()
            else:
                messages.add_message(request, messages.WARNING, f'An error occurred during getting username : {error}')
        else:
            messages.add_message(request, messages.WARNING, f'An error occurred during getting token : {error}')

        return HttpResponseRedirect(reverse('user:profile'))


class CreateGithubTokenView(LoginRequiredMixin, views.View):
    def get(self, request):
        return HttpResponseRedirect(get_login_url())


class GetRepositoryTreeView(views.View):
    def get(self, request, **kwargs):
        id = kwargs.get('id')
        repository = get_object_or_404(Repository, id=id)
        return JsonResponse(repository.get_repository_tree())


class GithubRepositoriesView(LoginRequiredMixin, views.View):
    def get(self, request):
        user = request.user
        error, repos = get_repository_list(user.github_token)
        repositories = []
        if not error:
            for repo in repos:
                repositories.append({
                    'name': repo.get('name'),
                    'url': repo.get('html_url'),
                    'description': repo.get('description'),
                    'id': repo.get('id')
                })
        else:
            messages.add_message(request, messages.WARNING, f'An error occurred when getting repositories : {error}')

        ctx = {
            'repositories': repositories
        }

        return render(request, 'github_integration/remote_repositories.html', context=ctx)


class RepositoriesView(LoginRequiredMixin, views.View):
    def get(self, request):
        repositories = request.user.repositories.all()
        ctx = {
            'repositories': repositories
        }

        return render(request, 'github_integration/repositories.html', context=ctx)


class RepositoryView(LoginRequiredMixin, views.View):
    def get(self, request, **kwargs):
        repository = get_object_or_404(Repository, id=kwargs.get('id'))
        if repository.user != request.user:
            raise PermissionDenied('You can not access this repository')

        ctx = {
            'branches': repository.branches.all()
        }
        return render(request, 'github_integration/repository.html', context=ctx)


class BranchView(LoginRequiredMixin, views.View):
    def get(self, request, **kwargs):
        repository = get_object_or_404(Repository, id=kwargs.get('id'))
        if repository.user != request.user:
            raise PermissionDenied('You can not access this repository')

        branch = repository.branches.get(repository=repository, commit_sha=kwargs.get('commit_sha'))
        path = kwargs.get('path')
        type_ = 'dir'

        if path:
            data = branch
            path = path.split('/')
            for p in path:
                data = get_object_or_404(data.content, name=p)

            if data.type == Content.FILE:
                type_ = 'file'
                error, blob = get_blob(request.user.github_token, data.url)
                if error is None:
                    text = blob.get('content')
                    encoding = blob.get('encoding')
                    if encoding == 'base64':
                        data = base64.b64decode(text).decode('utf-8')
                    elif encoding == 'utf-8':
                        data = text.decode('utf-8')
                    else:
                        pass
                    print(data)

            else:
                data = data.content.all()
        else:
            data = branch.content.all()

        ctx = {
            'data': data,
            'type': type_,
        }
        return render(request, 'github_integration/branch.html', context=ctx)
