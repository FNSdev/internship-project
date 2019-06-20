from django import views
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from user.forms import RegisterForm, LoginForm
from user.models import User
from github_integration.utils.token import is_token_valid


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
