from django import views
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import resolve, Resolver404
from user.forms import RegisterForm, LoginForm
from user.models import User
from github_integration.github_client_api.exceptions import GitHubApiRequestException, GitHubApiNotFound
from github_integration.github_client_api.github_client import GitHubClient


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
            return redirect('user:login')

        return render(request, 'user/register.html', {'form': form})


class LoginView(views.View):
    def get(self, request):
        ctx = {'form': LoginForm()}
        return render(request, 'user/login.html', context=ctx)

    def post(self, request):
        form = LoginForm(request.POST)
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            next_ = request.POST.get('next')
            try:
                resolve(next_)
                return redirect(next_)
            except Resolver404:
                return redirect('user:profile')

        return render(request, 'user/login.html', context={'form': form})


class ProfileView(LoginRequiredMixin, views.View):
    def get(self, request):
        user = request.user
        github_token_valid = False
        client = GitHubClient(user.github_token)
        try:
            github_token_valid = client.is_token_valid()
            messages.add_message(request, messages.INFO, 'Token was checked successfully')
        except GitHubApiRequestException as e:
            messages.add_message(request, messages.WARNING, f'An error occurred when checking token : {e.message}')

        ctx = {
            'github_token_valid': github_token_valid,
        }

        return render(request, 'user/profile.html', context=ctx)
