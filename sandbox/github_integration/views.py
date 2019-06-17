from django import views
from django.shortcuts import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from github_integration.utils.token import get_login_url, create_token, get_username
from github_integration.tasks import create_repository_task


class AddRepositoryView(LoginRequiredMixin, views.View):
    def post(self, request):
        repository_name = request.POST.get('repository')
        create_repository_task.delay(request.user.email, repository_name)
        return JsonResponse({'message': 'Task in queue'})


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
