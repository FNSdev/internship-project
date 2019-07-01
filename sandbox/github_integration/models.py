from django.db import models
from github_integration.github_client_api.exceptions import GitHubApiRequestException
from github_integration.github_client_api.parsers import parse_tree


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


class Repository(models.Model):
    UPDATED = 0
    UPDATE_IN_PROGRESS = 1
    DELETED_ON_GITHUB = 2

    STATUSES = (
        (UPDATED, 'updated'),
        (UPDATE_IN_PROGRESS, 'update_in_progress'),
        (DELETED_ON_GITHUB, 'deleted_on_github'),
    )

    name = models.CharField(max_length=150)
    url = models.URLField()
    status = models.IntegerField(choices=STATUSES, default=UPDATED)
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(
        to='user.User',
        on_delete=models.CASCADE,
        related_name='repositories',
    )

    def get_repository_tree(self):
        branches = []
        for branch in self.branches.all():
            content = branch.get_content()
            branches.append(
                {
                    'name': branch.name,
                    'commit sha': branch.commit_sha,
                    'url': branch.url,
                    'content': content
                }
            )

        tree = {
            'name': self.name,
            'owner': self.user.github_username,
            'status': self.get_status_display(),
            'url': self.url,
            'branches': branches
        }

        return tree

    def __str__(self):
        return self.name


class BranchManager(models.Manager):
    def create_branch_with_content(self, github_client, github_username, branch_name, url, repository, commit_sha):
        """
        Creates branch and populates it with content
        Exceptions need to be caught
        """

        new_branch = Branch(
            name=branch_name,
            url=url,
            repository=repository,
            commit_sha=commit_sha
        )
        new_branch.save()

        data = github_client.get_repository_tree(
            github_username,
            repository.name,
            commit_sha
        )

        tree = data.get('tree')
        parse_tree(tree, branch=new_branch)
        return new_branch



class Branch(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField()
    commit_sha = models.CharField(max_length=50)
    repository = models.ForeignKey(to=Repository, related_name='branches', on_delete=models.CASCADE)

    objects = BranchManager()

    def get_content(self, content=None):
        tree = []
        if content is None:
            content = self.content.all()
        for c in content:
            content_dict = {
                'name': c.name,
                'type': c.get_type_display(),
            }

            if c.type == Content.DIRECTORY:
                content_dict['content'] = self.get_content(content=c.content.all())
            tree.append(content_dict)

        return tree

    def __str__(self):
        return self.name
