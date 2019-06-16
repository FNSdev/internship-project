from django import views
from django.shortcuts import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from github_integration.utils.token import get_login_url, create_token, get_username
from github_integration.utils.repository import get_repository_info, get_repository_branches, get_repository_content
from github_integration.models import Repository, Branch, Content


class AddRepositoryView(LoginRequiredMixin, views.View):
    def post(self, request):
        user = request.user
        repository_name = request.POST.get('repository')

        repository = None

        error, repo = get_repository_info(user.github_token, user.github_username, repository_name)
        error_message = None

        if not error:
            repository = Repository(name=repo.get('name'), url=repo.get('html_url'))
            repository.save()
            error, branches = get_repository_branches(user.github_token, user.github_username, repository_name)
            if not error:
                for br in branches:
                    name = br.get('name')
                    url = '/'.join((repository.url, 'tree', name))
                    branch = Branch(name=name, url=url, repository=repository)
                    branch.save()
                    error, data = get_repository_content(
                        user.github_token,
                        user.github_username,
                        repository_name,
                        name)

                    if not error:
                        def parse_dir(directory, parent=None, top_level=False):
                            for c in directory:
                                type_ = Content.DIRECTORY if c.get('type') == 'dir' else Content.FILE
                                content = Content(
                                    name=c.get('name'),
                                    url=c.get('html_url'),
                                    type=type_
                                )
                                if top_level:
                                    content.branch = branch
                                if parent is not None:
                                    content.parent = parent
                                content.save()
                                if type_ == Content.DIRECTORY:
                                    parse_dir(c.get('content'), parent=content)

                        parse_dir(data, top_level=True)
                    else:
                        error_message = f'An error occurred when getting branch {name} content'

            else:
                error_message = 'An error occurred when getting repository branches'
        else:
            error_message = 'An error occurred when getting repository details'

        if error_message:
            messages.add_message(request, messages.WARNING, error_message)
            repository.delete()

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
