from django.urls import path
from core.views import IndexView, ProjectsView, ProjectView, ProjectSettingsView, InviteUserView, \
    InvitesView, CancelInviteView, AcceptInviteView, DeclineInviteView, RemoveUserView, CreateTaskView, \
    GetTasksView


app_name = 'core'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('invites', InvitesView.as_view(), name='invites'),
    path('invites/cancel/<int:id>', CancelInviteView.as_view(), name='cancel-invite'),
    path('invites/accept/<int:id>', AcceptInviteView.as_view(), name='accept-invite'),
    path('invites/decline/<int:id>', DeclineInviteView.as_view(), name='decline-invite'),
    path('projects', ProjectsView.as_view(), name='projects'),
    path('projects/<str:user>/<str:name>', ProjectView.as_view(), name='project'),
    path('projects/<str:user>/<str:name>/settings', ProjectSettingsView.as_view(), name='project_settings'),
    path('projects/<str:user>/<str:name>/settings/invite-user', InviteUserView.as_view(), name='invite'),
    path('projects/<str:user>/<str:name>/settings/remove-user/<str:email>', RemoveUserView.as_view(), name='invite'),
    path('projects/<str:user>/<str:name>/settings/create-task', CreateTaskView.as_view(), name='create_task'),
    path('projects/<str:user>/<str:name>/settings/get-tasks', GetTasksView.as_view(), name='get-tasks'),
]
