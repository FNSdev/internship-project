from django.db import models


class Content(models.Model):
    FILE = 0
    DIRECTORY = 1

    TYPES = (
        (FILE, 'file'),
        (DIRECTORY, 'dir'),
    )

    branch = models.ForeignKey(
        to='github_integration.Branch',
        related_name='content',
        on_delete=models.CASCADE,
        null=True
    )
    parent = models.ForeignKey(
        to='self',
        related_name='content',
        on_delete=models.CASCADE,
        null=True
    )
    type = models.IntegerField(choices=TYPES)
    name = models.CharField(max_length=150)
    url = models.URLField()

    def __str__(self):
        return self.name


# TODO make user field not nullable
class Repository(models.Model):
    UPDATED = 0
    UPDATE_IN_PROGRESS = 1

    STATUSES = (
        (UPDATED, 'updated'),
        (UPDATE_IN_PROGRESS, 'update_in_progress')
    )

    name = models.CharField(max_length=150)
    url = models.URLField()
    status = models.IntegerField(choices=STATUSES, default=UPDATED)
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(
        to='user.User',
        on_delete=models.CASCADE,
        related_name='repositories',
        null=True
    )

    def __str__(self):
        return self.name


class Branch(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField()
    commit_sha = models.CharField(max_length=50)
    repository = models.ForeignKey(to=Repository, related_name='branches', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
