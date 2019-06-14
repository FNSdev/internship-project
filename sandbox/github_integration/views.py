from django import views
from django.shortcuts import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from github_integration.utils.token import get_login_url, create_token, get_username
from github_integration.utils.repository import get_repository_info, get_repository_branches
from github_integration.models import Repository, Branch


class AddRepositoryView(LoginRequiredMixin, views.View):
    def post(self, request):
        user = request.user
        repository_name = request.POST.get('repository')

        error, repo = get_repository_info(user.github_token, user.github_username, repository_name)
        if not error:
            error, branches = get_repository_branches(user.github_token, user.github_username, repository_name)
            if not error:
                repository = Repository(name=repo.get('name'), url=repo.get('html_url'))
                repository.save()
                for br in branches:
                    name = br.get('name')
                    url = '/'.join((repository.url, 'tree', name))
                    branch = Branch(name=name, url=url, repository=repository)
                    branch.save()
            else:
                messages.add_message(request, messages.WARNING, 'An error occurred when getting repository branches')
        else:
            messages.add_message(request, messages.WARNING, 'An error occurred when getting repository details')

        return JsonResponse({})


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
