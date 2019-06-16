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
        null=True)
    parent = models.ForeignKey(
        to='self',
        related_name='content',
        on_delete=models.CASCADE,
        null=True)
    type = models.IntegerField(choices=TYPES)
    name = models.CharField(max_length=150)
    url = models.URLField()

    def __str__(self):
        return self.name


class Repository(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField()

    def __str__(self):
        return self.name


class Branch(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField()
    repository = models.ForeignKey(to=Repository, related_name='branches', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
