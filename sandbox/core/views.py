from django import views
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from core.forms import ProjectForm
from core.models import Project
import json


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
            'participating_objects': participating_projects,
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
            return JsonResponse({
                'message': 'Success',
                'project_name': project.name,
                'project_description': project.description,
                'project_url': '',
                'github_url': project.repository.url
            })
        else:
            data = form.errors.as_json()
            response = {
                'message': 'Error',
                'errors': json.loads(data)
            }
            print(response)
            return JsonResponse(response, status=400)
