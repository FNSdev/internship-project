import json
from django import views
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, reverse
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from core.forms import ProjectForm, InviteUserForm, TaskForm
from core.models import Project, Task, Invite
from user.models import User


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
        project = Project.objects.get_project_or_404(project_name, project_owner, user)

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


class GetActivitiesView(LoginRequiredMixin, views.View):
    # Returns required amount of activities

    def get(self, request, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']
        project = Project.objects.get_project_or_404(project_name, project_owner, user)

        count = request.GET.get('count')
        p = Paginator(project.activities.all(), count)
        page = p.page(1)

        response = {'activities': []}
        for activity in page.object_list:
            response['activities'].append(activity.get_html())

        return JsonResponse(response)


class ProjectSettingsView(LoginRequiredMixin, views.View):
    def get(self, request, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']

        project = Project.objects.get_project_or_404_or_403(project_name, project_owner, user.email)
        task_form = TaskForm(
            initial={
                'project': project,
                'task_type': Task.TASK,
                'parent_task': None
            },
        )
        task_form.fields['assignees'].queryset = project.team.all()
        task_form.fields['branches'].queryset = project.repository.branches.all()

        ctx = {
            'project': project,
            'invite_user_form': InviteUserForm(),
            'task_form': task_form,
        }
        return HttpResponse(render(request, 'core/project_settings.html', context=ctx))


class GetTasksView(LoginRequiredMixin, views.View):
    """Returns required amount of tasks"""

    def get(self, request, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']
        project = Project.objects.get_project_or_404(project_name, project_owner, user)

        count = request.GET.get('count')
        if user == project.owner:
            qs = project.tasks.all()
        else:
            qs = project.tasks.filter(assignees=user)

        p = Paginator(qs, count)
        page = p.page(1)

        response = {'tasks': []}
        for task in page.object_list:
            response['tasks'].append({
                'name': task.name,
                'status': task.get_status_display(),
                'priority': task.get_priority_display(),
                'progress': task.get_progress(),
                'deadline': task.deadline,
                'url': reverse(
                    'core:task',
                    kwargs={
                        'user': project_owner,
                        'name': project_name,
                        'task_id': task.task_id,
                    }
                )
            })

        return JsonResponse(response)


class CreateTaskView(LoginRequiredMixin, views.View):
    def post(self, request, **kwargs):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            task.on_created()

            return JsonResponse({
                'message': 'Success',
            })
        else:
            data = form.errors.as_json()
            response = {
                'message': 'Error',
                'errors': json.loads(data)
            }
            return JsonResponse(response, status=400)


class TaskView(LoginRequiredMixin, views.View):
    def get(self, request, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']
        project = Project.objects.get_project_or_404(project_name, project_owner, user)
        task = get_object_or_404(project.tasks.all(), task_id=kwargs['task_id'])

        sub_task_form = TaskForm(
            initial={
                'project': project,
                'task_type': Task.SUB_TASK,
                'parent_task': task
            }
        )
        sub_task_form.fields['branches'].queryset = project.repository.branches.all()

        task_form = TaskForm(instance=task)
        task_form.fields['branches'].queryset = project.repository.branches.all()

        return HttpResponse(
            render(
                request,
                'core/task.html',
                context={
                    'task': task,
                    'branches': task.branches.all(),
                    'sub_task_form': sub_task_form,
                    'task_form': task_form,
                }
            )
        )


class UpdateTaskView(LoginRequiredMixin, views.View):
    def post(self, request, *args, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']
        project = Project.objects.get_project_or_404(project_name, project_owner, user)

        task = get_object_or_404(project.tasks.all(), task_id=kwargs['task_id'])
        old_fields = model_to_dict(task)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()

            if task.status == Task.COMPLETED:
                task.on_completed()
            else:
                difference = task.get_difference(old_fields)
                task.on_updated(difference)

            return JsonResponse({'message': 'Updated'})
        else:
            data = form.errors.as_json()
            response = {
                'message': 'Error',
                'errors': json.loads(data)
            }
            return JsonResponse(response, status=400)


class GetSubTasksView(LoginRequiredMixin, views.View):
    """Returns required amount of task's sub_tasks"""

    def get(self, request, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']
        project = Project.objects.get_project_or_404(project_name, project_owner, user)

        task = get_object_or_404(project.tasks.all(), task_id=kwargs['task_id'])
        count = request.GET.get('count')
        p = Paginator(task.sub_tasks.all(), count)
        page = p.page(1)

        response = {'tasks': []}
        for task in page.object_list:
            response['tasks'].append({
                'name': task.name,
                'status': task.get_status_display(),
                'priority': task.get_priority_display(),
                'branches': [{'name': branch.name, 'url': branch.url} for branch in task.branches.all()],
                'deadline': task.deadline
            })

        return JsonResponse(response)


class InviteUserView(LoginRequiredMixin, views.View):
    def post(self, request, **kwargs):
        form = InviteUserForm(request.POST)
        if form.is_valid():
            user = request.user
            project_name = kwargs['name']
            project_owner = kwargs['user']

            project = Project.objects.get_project_or_404_or_403(project_name, project_owner, user.email)

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


class RemoveUserView(LoginRequiredMixin, views.View):
    def post(self, request, **kwargs):
        user = request.user
        project_name = kwargs['name']
        project_owner = kwargs['user']

        project = Project.objects.get_project_or_404_or_403(project_name, project_owner, user.email)
        user_to_remove = get_object_or_404(project.team.all(), email=kwargs['email'])

        if user_to_remove == project.owner:
            return JsonResponse({'message': 'You can not remove yourself', 'status': 'error'})

        project.team.remove(user_to_remove)
        project.save()

        try:
            invite = Invite.objects.get(to__email=kwargs['email'], project=project)
            invite.delete()
        except Invite.DoesNotExist:
            pass

        return JsonResponse({'message': 'Success', 'status': 'ok'})


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
