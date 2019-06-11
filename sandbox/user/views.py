from django import views
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from user.forms import RegisterForm, LoginForm
from user.models import User


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
        print(user)
        if user is not None:
            login(request, user)
            return redirect('core:index')

        form = LoginForm()
        return render(request, 'user/login.html', context={'form': form})
