from django.urls import path
from user.views import RegisterView, LoginView, ProfileView, GetGithubTokenView, CreateGithubTokenView
from django.contrib.auth.views import LogoutView


app_name = 'user'
urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('get-github-token', GetGithubTokenView.as_view(), name='get_github_token'),
    path('create-github-token', CreateGithubTokenView.as_view(), name='create_github_token'),
]
