import base64
from django import views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from user.forms import RegisterForm, LoginForm
from user.models import User
from github_integration.models import Repository, Branch, Content
from github_integration.utils.token import is_token_valid
from github_integration.utils.repository import get_repository_list, get_blob


class RegisterView(views.View):
    def get(self, request):
        ctx = {'form': RegisterForm()}
        return render(request, 'user/register.html', context=ctx)

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User(
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data['phone_number'],
                date_of_birth=data['date_of_birth'],
                password=make_password(data['password1']),
            )
            user.save()
            return redirect('core:index')

        form = RegisterForm()
        return render(request, 'user/register.html', {'form': form})


class LoginView(views.View):
    def get(self, request):
        ctx = {'form': LoginForm()}
        return render(request, 'user/login.html', context=ctx)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:index')

        form = LoginForm()
        return render(request, 'user/login.html', context={'form': form})


class ProfileView(LoginRequiredMixin, views.View):
    def get(self, request):
        user = request.user
        error, github_token_valid = is_token_valid(user.github_token)
        if not error:
            messages.add_message(request, messages.INFO, 'Token was checked successfully')
        else:
            messages.add_message(request, messages.WARNING, f'An error occurred when checking token : {error}')

        ctx = {
            'github_token_valid': github_token_valid,
        }

        return render(request, 'user/profile.html', context=ctx)


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

        return render(request, 'user/remote_repositories.html', context=ctx)


class RepositoriesView(LoginRequiredMixin, views.View):
    def get(self, request):
        repositories = request.user.repositories.all()
        ctx = {
            'repositories': repositories
        }

        return render(request, 'user/repositories.html', context=ctx)


class RepositoryView(LoginRequiredMixin, views.View):
    def get(self, request, **kwargs):
        repository = get_object_or_404(Repository, id=kwargs.get('id'))
        if repository.user != request.user:
            raise PermissionDenied('You can not access this repository')

        ctx = {
            'branches': repository.branches.all()
        }
        return render(request, 'user/repository.html', context=ctx)


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
        return render(request, 'user/branch.html', context=ctx)
