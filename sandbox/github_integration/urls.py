from django.urls import path
from github_integration.views import AddRepositoryView, GetGithubTokenView, CreateGithubTokenView, \
    GetRepositoryTreeView, GetTaskStatusView


app_name = 'github_integration'
urlpatterns = [
    path('add-repository', AddRepositoryView.as_view(), name='add_repository'),
    path('get-github-token', GetGithubTokenView.as_view(), name='get_github_token'),
    path('create-github-token', CreateGithubTokenView.as_view(), name='create_github_token'),
    path('get-repository-tree/<int:id>', GetRepositoryTreeView.as_view(), name='get_repository_tree'),
    path('get-task-status', GetTaskStatusView.as_view(), name='get_task_status'),
]
