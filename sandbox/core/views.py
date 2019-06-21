from django import views
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from core.forms import ProjectForm, InviteUserForm
from core.models import Project, Invite
from user.models import User
import json


def temp_get_project_or_404_or_403(project_name, project_owner, user):
    if project_owner != user.email:
        raise PermissionDenied

    project = get_object_or_404(
        Project.objects.prefetch_related('team', 'tasks'),
        owner__email=project_owner,
        name=project_name)

    return project


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx


class ProjectsView(LoginRequiredMixin, views.View):
    def get(self, request):
        user = request.user
        owned_projects = user.owned_projects.all()
        participating_projects = user.participating_projects.all()
        form = ProjectForm()
        form.fields['repository'].queryset = user.repositories.all()

        ctx = {
            'owned_projects': owned_projects,
            'participating_projects': participating_projects,
            'form': form
        }

        return HttpResponse(render(request, 'core/projects.html', context=ctx))

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            project = Project(
                name=data['name'],
                description=data['description'],
                repository=data['repository'],
                owner=request.user)
            project.save()
            project.team.add(request.user)
            project.save()
            return JsonResponse({
                'message': 'Success',
                'project_name': project.name,
                'project_description': project.description,
                'project_url': '/'.join((request.get_full_path(), request.user.email, project.name)),
                'github_url': project.repository.url
            })
        else:
            data = form.errors.as_json()
            response = {
                'message': 'Error',
                'errors': json.loads(data)
            }
            return JsonResponse(response, status=400)


class ProjectView(LoginRequiredMixin, views.View):
    def get(self, request, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']
        project = get_object_or_404(
            Project.objects.prefetch_related('team', 'tasks'),
            owner__email=project_owner,
            name=project_name)

        team = project.team.all()
        if user not in team:
            raise Http404

        user_tasks = project.tasks.filter(assignees=user)

        ctx = {
            'project': project,
            'team': team,
            'user_tasks': user_tasks,
            'is_owner': user.email == project_owner,
        }

        return HttpResponse(render(request, 'core/project.html', context=ctx))


class ProjectSettingsView(LoginRequiredMixin, views.View):
    def get(self, request, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']

        project = temp_get_project_or_404_or_403(project_name, project_owner, user)

        ctx = {
            'project': project,
            'invite_user_form': InviteUserForm()
        }
        return HttpResponse(render(request, 'core/project_settings.html', context=ctx))


class InviteUserView(LoginRequiredMixin, views.View):
    def post(self, request, **kwargs):
        form = InviteUserForm(request.POST)
        if form.is_valid():
            user = request.user
            project_name = kwargs['name']
            project_owner = kwargs['user']

            project = temp_get_project_or_404_or_403(project_name, project_owner, user)

            data = form.cleaned_data
            try:
                invited_user = User.objects.get(email=data['email'])
            except User.DoesNotExist:
                return JsonResponse({'message': f'User {data["email"]} does not exist'})

            if invited_user in project.team.all():
                return JsonResponse({'message': f'User {data["email"]} is already part of your team'})
            if Invite.objects.filter(project=project, to=invited_user):
                return JsonResponse({'message': f'User {data["email"]} is already invited'})

            invite = Invite(
                to=invited_user,
                by=user,
                message=data['message'],
                project=project,
            )
            invite.save()

            return JsonResponse({'message': 'Success'})
        else:
            data = form.errors.as_json()
            response = {
                'message': 'Error',
                'errors': json.loads(data)
            }
            return JsonResponse(response, status=400)


class InvitesView(LoginRequiredMixin, views.View):
    def get(self, request):
        user = request.user
        received_invites = Invite.objects.filter(to=user)
        sent_invites = Invite.objects.filter(by=user)

        ctx = {
            'received_invites': received_invites,
            'sent_invites': sent_invites
        }
        return HttpResponse(render(request, 'core/invites.html', context=ctx))


class CancelInviteView(LoginRequiredMixin, views.View):
    def post(self, request, **kwargs):
        invite = get_object_or_404(request.user.sent_invites, id=kwargs['id'])
        invite.delete()
        return JsonResponse({'message': 'Success'})


class AcceptInviteView(LoginRequiredMixin, views.View):
    def post(self, request, **kwargs):
        invite = get_object_or_404(request.user.received_invites, id=kwargs['id'])
        invite.accept()
        return JsonResponse({'message': 'Success'})


class DeclineInviteView(LoginRequiredMixin, views.View):
    def post(self, request, **kwargs):
        invite = get_object_or_404(request.user.received_invites, id=kwargs['id'])
        invite.decline()
        return JsonResponse({'message': 'Success'})
