from django import views
from django.shortcuts import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from github_integration.utils.token import get_login_url, create_token, get_username
from github_integration.tasks import create_repository_task
from github_integration.models import Repository
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
