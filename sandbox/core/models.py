from django.db import models


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
        (COMPLETED, 'completed')
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

    def __str__(self):
        return f'{self.project.name} / tasks / {self.name}'


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
