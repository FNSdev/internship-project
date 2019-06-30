from core.models import Task, Project
from user.models import User
from api.serializers import UserSerializer, ProjectSerializer, TaskSerializer
from api.permissions import IsProjectOwner
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'email'
    lookup_value_regex = r'[\w@.]+'
    serializer_class = UserSerializer
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    authentication_classes = (SessionAuthentication, )

    def get_queryset(self):
        owner_email = self.kwargs['owner_email']
        owner = get_object_or_404(
            User.objects.all(),
            email=owner_email,
        )
        if self.request.user.email != owner_email:
            return self.queryset.filter(
                Q(owner=owner),
                Q(public=True) | Q(team=self.request.user)
            )
        return self.request.filter(owner=owner)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes.append(IsProjectOwner)

        return [permission() for permission in permission_classes]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        owner_email = self.kwargs['owner_email']
        project_name = self.kwargs['project_name']
        project = Project.objects.get_project_or_404_or_403(
            project_name,
            owner_email,
            self.request.user.email
        )
        return self.queryset.filter(
            project=project
        )
