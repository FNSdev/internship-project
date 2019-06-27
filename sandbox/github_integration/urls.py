from django.urls import path, re_path
from github_integration.views import AddRepositoryView, GetGithubTokenView, CreateGithubTokenView, \
    GetRepositoryTreeView, GetCeleryTaskStatusView, GithubRepositoriesView, RepositoriesView, \
    RepositoryView, BranchView


app_name = 'github_integration'
urlpatterns = [
    path('add-repository', AddRepositoryView.as_view(), name='add_repository'),
    path('get-github-token', GetGithubTokenView.as_view(), name='get_github_token'),
    path('create-github-token', CreateGithubTokenView.as_view(), name='create_github_token'),
    path('get-repository-tree/<int:id>', GetRepositoryTreeView.as_view(), name='get_repository_tree'),
    path('get-celery-task-status', GetCeleryTaskStatusView.as_view(), name='get_celery-task_status'),
    path('github-repositories', GithubRepositoriesView.as_view(), name='github_repositories'),
    path('repositories', RepositoriesView.as_view(), name='repositories'),
    path('repository/<int:id>', RepositoryView.as_view(), name='repository'),
    path('repository/<int:id>/<str:commit_sha>', BranchView.as_view(), name='branch'),
    re_path(
        r'^repository/(?P<id>[0-9]+)/(?P<commit_sha>[a-z 0-9]+)/(?P<path>(.(/)?)*)$',
        BranchView.as_view(),
        name='branch_content'),
]
