from django.urls import path, re_path
from user.views import RegisterView, LoginView, ProfileView, GithubRepositoriesView, RepositoriesView, \
    RepositoryView, BranchView
from django.contrib.auth.views import LogoutView


app_name = 'user'
urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('github-repositories', GithubRepositoriesView.as_view(), name='github_repositories'),
    path('repositories', RepositoriesView.as_view(), name='repositories'),
    path('repository/<int:id>', RepositoryView.as_view(), name='repository'),
    path('repository/<int:id>/<str:commit_sha>', BranchView.as_view(), name='branch'),
    re_path(
        r'^repository/(?P<id>[0-9]+)/(?P<commit_sha>[a-z 0-9]+)/(?P<path>(.(/)?)*)$',
        BranchView.as_view(),
        name='branch_content'),
]
