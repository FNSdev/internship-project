import requests
from django import views
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from user.forms import RegisterForm, LoginForm
from user.models import User
from sandbox import settings


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
        return render(request, 'user/profile.html')


class GetGithubTokenView(LoginRequiredMixin, views.View):
    def get(self, request):
        code = request.GET.get('code')
        if code:
            response = requests.post(
                settings.GITHUB_GET_TOKEN_URL,
                json={
                    'code': code,
                    'client_id': settings.GITHUB_CLIENT_ID,
                    'client_secret': settings.GITHUB_CLIENT_SECRET
                },
                headers={
                    'Accept': 'application/json'
                }
            )
            if response.status_code == 200:
                response = response.json()
                if not response.get('error'):
                    token = response.get('access_token')
                    user = request.user
                    user.github_token = token
                    user.save()
        return HttpResponseRedirect(reverse('core:index'))


class CreateGithubTokenView(LoginRequiredMixin, views.View):
    def get(self, request):
        return HttpResponseRedirect(f'{settings.GITHUB_LOGIN_URL}?client_id={settings.GITHUB_CLIENT_ID}&scope=user%20repo')
