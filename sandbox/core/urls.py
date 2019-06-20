from django.urls import path
from core.views import IndexView, ProjectsView


app_name = 'core'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('projects', ProjectsView.as_view(), name='projects'),
]
