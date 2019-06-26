from django.db import models
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import JSONField
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string


class ProjectManager(models.Manager):
    def get_project_or_404_or_403(self, project_name, owner_email, user_email):
        """Returns project if it is accessed by its owner"""

        project = get_object_or_404(
            Project.objects.prefetch_related('tasks', 'team', 'repository'),
            owner__email=owner_email,
            name=project_name,
        )
        if owner_email == user_email:
            return project
        else:
            raise PermissionDenied

    def get_project_or_404(self, project_name, owner_email, user):
        """Returns a project if it is public or raises 404 if user is not in the project's team"""

        project = get_object_or_404(
            Project.objects.prefetch_related('tasks', 'team', 'repository'),
            owner__email=owner_email,
            name=project_name,
        )

        if project.public or user in project.team.all():
            return project
        raise Http404


class Project(models.Model):
    repository = models.OneToOneField(
        to='github_integration.Repository',
        on_delete=models.DO_NOTHING)

    owner = models.ForeignKey(
        to='user.User',
        related_name='owned_projects',
        on_delete=models.CASCADE
    )
    team = models.ManyToManyField(
        to='user.User',
        related_name='participating_projects'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    public = models.BooleanField(default=False)
    auto_sync_with_github = models.BooleanField(default=False)
    tasks_count = models.PositiveIntegerField(default=0)

    objects = ProjectManager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = '-'.join(self.name.split())
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f'{self.owner} : {self.name}'


class Task(models.Model):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    BLOCK = 3

    PENDING = 0
    IN_PROGRESS = 1
    IN_REVIEW = 2
    COMPLETED = 3

    TASK = 0
    SUB_TASK = 1

    PRIORITIES = (
        (LOW, 'low'),
        (MEDIUM, 'medium'),
        (HIGH, 'high'),
        (BLOCK, 'block'),
    )

    STATUSES = (
        (PENDING, 'pending'),
        (IN_PROGRESS, 'in progress'),
        (IN_REVIEW, 'in review'),
        (COMPLETED, 'completed'),
    )

    TYPES = (
        (TASK, 'task'),
        (SUB_TASK, 'sub_task'),
    )

    project = models.ForeignKey(
        to='core.Project',
        related_name='tasks'
        , on_delete=models.CASCADE
    )
    assignees = models.ManyToManyField(
        to='user.User',
        related_name='tasks'
    )
    branches = models.ManyToManyField(
        to='github_integration.Branch',
        related_name='tasks',
        blank=True
    )
    parent_task = models.ForeignKey(
        to='self',
        related_name='sub_tasks',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    deadline = models.DateField(blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITIES, default=MEDIUM)
    status = models.IntegerField(choices=STATUSES, default=PENDING)
    task_type = models.IntegerField(choices=TYPES, default=TASK)
    task_id = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-priority', 'deadline', 'status']

    def __str__(self):
        return f'{self.project.name} / task_{self.task_id} : {self.name}'

    def save(self, *args, **kwargs):
        # sub_task can not have sub_tasks
        if self.parent_task is not None:
            if self.task_type == self.SUB_TASK and self.parent_task.task_type == self.SUB_TASK:
                raise ValidationError('Sub Tasks can not have sub tasks')
        if not self.id:
            # If task is new, give it unique per project id
            self.project.tasks_count += 1
            self.project.save()
            self.task_id = self.project.tasks_count

            # If auto-sync is enabled, try to find related branches
            project = self.project
            repo = project.repository
            if repo.status != repo.UPDATE_IN_PROGRESS and project.auto_sync_with_github:
                branches = project.repository.branches.filter(name__icontains=f'task_{self.task_id}/')
                if branches.count() > 0:
                    super().save(*args, **kwargs)
                    self.branches.add(*branches)

        super().save(*args, **kwargs)

    def on_created(self):
        """Creates required Activity object"""

        Activity.objects.create(
            activity_type=Activity.TASK_WAS_CREATED,
            related_object=self,
            context={},
            project=self.project,
        )

    def on_updated(self, difference):
        """Creates required Activity object"""

        Activity.objects.create(
            activity_type=Activity.TASK_WAS_UPDATED,
            related_object=self,
            context={
                'difference': difference
            },
            project=self.project,
        )

    def on_completed(self):
        """Creates required Activity object"""

        Activity.objects.create(
            activity_type=Activity.TASK_WAS_COMPLETED,
            related_object=self,
            context={},
            project=self.project,
        )

    def get_progress(self):
        if self.status == self.COMPLETED:
            return 100
        sub_tasks_count = self.sub_tasks.count()
        if sub_tasks_count == 0:
            return 0
        completed_sub_tasks_count = self.sub_tasks.filter(status=self.COMPLETED).count()
        return round((completed_sub_tasks_count / sub_tasks_count) * 100, 2)

    def get_difference(self, other_fields: dict):
        """Returns difference between this Task and other task field's content"""

        difference = []
        fields = model_to_dict(self)

        for k, v in other_fields.items():
            if fields[k] != v:
                if k == 'status':
                    changed_from = self.STATUSES[v][1]
                    changed_to = self.STATUSES[fields[k]][1]
                elif k == 'priority':
                    changed_from = self.PRIORITIES[v][1]
                    changed_to = self.PRIORITIES[fields[k]][1]
                elif k == 'assignees':
                    changed_from = [user.email for user in other_fields[k]]
                    changed_to = [user.email for user in self.assignees.all()]
                elif k == 'branches':
                    changed_from = [branch.name for branch in other_fields[k]]
                    changed_to = [branch.name for branch in self.branches.all()]
                else:
                    changed_from = other_fields[k]
                    changed_to = fields[k]
                difference.append({
                    'field': k,
                    'changed_from': changed_from,
                    'changed_to': changed_to
                })

        return difference


class Invite(models.Model):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2

    STATUSES = (
        (PENDING, 'pending'),
        (ACCEPTED, 'accepted'),
        (DECLINED, 'declined'),
    )

    to = models.ForeignKey(to='user.User', related_name='received_invites', on_delete=models.CASCADE)
    by = models.ForeignKey(to='user.User', related_name='sent_invites', on_delete=models.CASCADE)
    project = models.ForeignKey(to='core.Project', related_name='invites', on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    status = models.IntegerField(choices=STATUSES, default=PENDING)

    def __str__(self):
        return f'{self.project.name} : from {self.by} to {self.to}'

    def accept(self):
        self.status = Invite.ACCEPTED
        self.save()
        self.project.team.add(self.to)
        self.project.save()

    def decline(self):
        self.status = Invite.DECLINED
        self.save()


class Activity(models.Model):
    TASK_WAS_CREATED = 'TASK_WAS_CREATED'
    TASK_WAS_UPDATED = 'TASK_WAS_UPDATED'
    TASK_WAS_COMPLETED = 'TASK_WAS_COMPLETED'
    BRANCH_WAS_UPDATED = 'BRANCH_WAS_UPDATED'
    UNKNOWN_ACTIVITY = 'UNKNOWN_ACTIVITY'

    TYPES = (
        (TASK_WAS_CREATED, 'task was created'),
        (TASK_WAS_UPDATED, 'task was updated'),
        (TASK_WAS_COMPLETED, 'task was completed'),
        (BRANCH_WAS_UPDATED, 'branch was updated'),
        (UNKNOWN_ACTIVITY, 'unknown activity'),
    )

    TEMPLATES = {
        TASK_WAS_CREATED: 'core/activities/task_created.html',
        TASK_WAS_UPDATED: 'core/activities/task_updated.html',
        TASK_WAS_COMPLETED: 'core/activities/task_completed.html',
        BRANCH_WAS_UPDATED: 'core/activities/branch_updated.html',
    }

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey()
    activity_type = models.CharField(choices=TYPES, default=UNKNOWN_ACTIVITY, max_length=50)
    context = JSONField()
    date_time = models.DateTimeField(auto_now_add=True, null=True)
    project = models.ForeignKey(
        to='core.Project',
        related_name='activities',
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        ordering = ['-date_time', 'activity_type']

    def get_html(self):
        """Returns an html representation of activity depending on related object type and activity type"""

        return render_to_string(
            self.TEMPLATES[self.activity_type],
            context={
                'activity': self,
            }
        )

    def __str__(self):
        if self.content_type.name == 'task':
            task = self.related_object
            if self.activity_type == self.TASK_WAS_CREATED:
                return f'{task} was created'
            elif self.activity_type == self.TASK_WAS_UPDATED:
                return f'{task} was updated'
            elif self.activity_type == self.TASK_WAS_COMPLETED:
                return f'{task} was completed'
            else:
                return 'Unknown task activity'
        elif self.content_type.name == 'branch':
            branch = self.related_object
            if self.activity_type == self.BRANCH_WAS_UPDATED:
                return f'Branch {branch} was updated'
            else:
                return 'Unknown branch activity'
        else:
            return 'Unknown activity'
