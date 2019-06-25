from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import HStoreField
from django.forms.models import model_to_dict
from django.shortcuts import reverse


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
        if self.parent_task is not None:
            if self.task_type == self.SUB_TASK and self.parent_task.task_type == self.SUB_TASK:
                raise ValidationError('Sub Tasks can not have sub tasks')
        if not self.id:
            self.project.tasks_count += 1
            self.project.save()
            self.task_id = self.project.tasks_count
            project = self.project
            repo = project.repository
            if repo.status != repo.UPDATE_IN_PROGRESS and project.auto_sync_with_github:
                branches = project.repository.branches.filter(name__icontains=f'task_{self.task_id}/')
                if branches.count() > 0:
                    super().save(*args, **kwargs)
                    self.branches.add(*branches)

        super().save(*args, **kwargs)

    def on_created(self):
        Activity.objects.create(
            activity_type=Activity.TASK_WAS_CREATED,
            related_object=self,
            context={},
            project=self.project,
        )

    def on_updated(self, difference):
        Activity.objects.create(
            activity_type=Activity.TASK_WAS_UPDATED,
            related_object=self,
            context={
                'difference': difference
            },
            project=self.project,
        )

    def on_completed(self):
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

    def get_difference(self, other_fields):
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
                difference.append(
                    (
                        f'<li><mark>{k}</mark> field was changed <b>from</b> <mark>{changed_from}</mark> '
                        f'<b>to</b> <mark>{changed_to}</mark></li>'
                    )
                )

        return ''.join(difference)


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
    TASK_WAS_CREATED = 0
    TASK_WAS_UPDATED = 1
    TASK_WAS_COMPLETED = 2
    BRANCH_WAS_UPDATED = 3

    TYPES = (
        (TASK_WAS_CREATED, 'task was created'),
        (TASK_WAS_UPDATED, 'task was updated'),
        (TASK_WAS_COMPLETED, 'task was completed'),
        (BRANCH_WAS_UPDATED, 'branch was updated'),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey()
    activity_type = models.IntegerField(choices=TYPES)
    context = HStoreField()
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
        if self.content_type.name == 'task':
            if self.activity_type == self.TASK_WAS_CREATED:
                html = (
                    '<tr>'
                    f'<td>{self.date_time}</td>'
                    f'<td>{self.get_activity_type_display()}</td>'
                    f'<td><b>{self.related_object.name} Task</b> was created</td>'
                    '</tr>'
                )
                return html
            elif self.activity_type == self.TASK_WAS_UPDATED:
                html = (
                    '<tr>'
                    f'<td>{self.date_time}</td>'
                    f'<td>{self.get_activity_type_display()}</td>'
                    f'<td><b>{self.related_object.name} Task</b> was updated.'
                    f' Changes: <ul>{self.context["difference"]}</ul></tr>'
                )
                return html
            elif self.activity_type == self.TASK_WAS_COMPLETED:
                html = (
                    '<tr>'
                    f'<td>{self.date_time}</td>'
                    f'<td>{self.get_activity_type_display()}</td>'
                    f'<td><b>{self.related_object.name} Task</b> was completed</td>'
                    '</tr>'
                )
                return html
            else:
                return 'Unknown task activity'
        elif self.content_type.name == 'branch':
            if self.activity_type == self.BRANCH_WAS_UPDATED:
                pass
            else:
                return 'Unknown branch activity'
        else:
            return 'Unknown activity'

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
