from django.urls import path
from core.views import (
    IndexView,
    ProjectsView,
    ProjectView,
    ProjectSettingsView,
    InviteUserView,
    InvitesView,
    CancelInviteView,
    AcceptInviteView,
    DeclineInviteView,
    RemoveUserView,
    CreateTaskView,
    GetTasksView,
    TaskView,
    GetSubTasksView,
    CreateSubTaskView,
    UpdateTaskView,
    GetActivitiesView
)


app_name = 'core'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('invites', InvitesView.as_view(), name='invites'),
    path('invites/cancel/<int:id>', CancelInviteView.as_view(), name='cancel-invite'),
    path('invites/accept/<int:id>', AcceptInviteView.as_view(), name='accept-invite'),
    path('invites/decline/<int:id>', DeclineInviteView.as_view(), name='decline-invite'),
    path('projects', ProjectsView.as_view(), name='projects'),
    path('projects/<str:user>/<str:name>', ProjectView.as_view(), name='project'),
    path('projects/<str:user>/<str:name>/get-activities', GetActivitiesView.as_view(), name='get-activities'),
    path('projects/<str:user>/<str:name>/settings', ProjectSettingsView.as_view(), name='project_settings'),
    path('projects/<str:user>/<str:name>/settings/invite-user', InviteUserView.as_view(), name='invite'),
    path('projects/<str:user>/<str:name>/settings/remove-user/<str:email>', RemoveUserView.as_view(), name='invite'),
    path('projects/<str:user>/<str:name>/settings/create-task', CreateTaskView.as_view(), name='create_task'),
    path('projects/<str:user>/<str:name>/settings/get-tasks', GetTasksView.as_view(), name='get-tasks'),
    path('projects/<str:user>/<str:name>/tasks/<int:task_id>', TaskView.as_view(), name='task'),
    path(
        'projects/<str:user>/<str:name>/tasks/<int:task_id>/get-sub-tasks',
        GetSubTasksView.as_view(),
        name='get_sub_tasks'
    ),
    path(
        'projects/<str:user>/<str:name>/tasks/<int:task_id>/create-sub-task',
        CreateSubTaskView.as_view(),
        name='create-sub-task'
    ),
    path('projects/<str:user>/<str:name>/tasks/<int:task_id>/update', UpdateTaskView.as_view(), name='update-task'),
]
