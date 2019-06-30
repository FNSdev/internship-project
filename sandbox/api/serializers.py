from core.models import Task, Project
from user.models import User
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'name',
            'task_type',
            'priority',
            'status',
            'deadline',
            'description',
        )


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'name',
            'description',
        )


class UserSerializer(serializers.ModelSerializer):
    # owned_projects = ProjectSerializer(many=True)
    # participating_projects = ProjectSerializer(many=True)

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'github_username',
            # 'owned_projects',
            # 'participating_projects',
        )
