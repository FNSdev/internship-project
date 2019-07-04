import base64
from django.shortcuts import get_object_or_404
from github_integration.github_client_api.exceptions import GitHubApiRequestException
from github_integration.github_client_api.github_client import GitHubClient


def parse_tree(subtree, level=1, parent=None, branch=None):
    """
    Parses a repository tree that was received from GitHub API and creates Content objects.

    Logic in this method is required, because GitHub API gives us tree in a flat format,
    and we need to build a hierarchy from it.
    """
    from github_integration.models import Content

    for i, node in enumerate(subtree):
        if not node.get('processed'):
            path = node.get('path').split('/')
            if len(path) == level:
                content_name = path[-1]
                type_ = Content.DIRECTORY if node.get('type') == 'tree' else Content.FILE

                content = Content(
                    name=content_name,
                    url=node.get('url'),
                    type=type_
                )

                if branch:
                    content.branch = branch
                if parent:
                    content.parent = parent
                content.save()

                if type_ == Content.DIRECTORY:
                    parse_tree(subtree[(i + 1):], level=(level + 1), parent=content)
                node['processed'] = True
            else:
                break


def parse_path(token, path, branch):
    content_type = 'dir'
    # Check if we are not on a top level of hierarchy
    if path:
        from github_integration.models import Content
        data = branch

        # Get required content
        path = path.split('/')
        for p in path:
            data = get_object_or_404(data.content, name=p)

        # If content is a file, get it's text
        if data.type == Content.FILE:
            content_type = 'file'
            client = GitHubClient(token)
            try:
                blob = client.get_blob(data.url)
                text = blob.get('content')
                encoding = blob.get('encoding')
                if encoding == 'base64':
                    data = base64.b64decode(text).decode('utf-8')
                elif encoding == 'utf-8':
                    data = text.decode('utf-8')
                else:
                    pass
            except GitHubApiRequestException:
                # TODO write to log
                print('Request Exception')
        else:
            data = data.content.all()
    else:
        data = branch.content.all()

    return content_type, data
