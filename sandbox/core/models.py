from django.db import models
from django.core.exceptions import ValidationError


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
        related_name='tasks'
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
        if self.task_type == self.SUB_TASK and self.sub_tasks.count() != 0:
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

    def get_progress(self):
        if self.status == self.COMPLETED:
            return 100
        sub_tasks_count = self.sub_tasks.count()
        if sub_tasks_count == 0:
            return 0
        completed_sub_tasks_count = self.sub_tasks.filter(status=self.COMPLETED)
        return round((completed_sub_tasks_count / sub_tasks_count) * 100, 2)


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
