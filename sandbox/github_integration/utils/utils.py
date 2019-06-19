from github_integration.models import Content
from github_integration.utils.repository import get_repository_tree
from github_integration.models import Branch


def create_branch(user, name, url, repository, commit_sha):
    new_branch = Branch(
        name=name,
        url=url,
        repository=repository,
        commit_sha=commit_sha
    )
    new_branch.save()

    error, data = get_repository_tree(
        user.github_token,
        user.github_username,
        repository.name,
        commit_sha
    )

    if error is None:
        tree = data.get('tree')
        parse_tree(tree, branch=new_branch)
        return new_branch
    else:
        return error


def parse_tree(subtree, level=1, parent=None, branch=None):
    for i, node in enumerate(subtree):
        if node.get('processed') is None:
            path = node.get('path').split('/')
            if len(path) == level:
                content_name = path[-1]
                type_ = Content.DIRECTORY if node.get('type') == 'tree' else Content.FILE

                content = Content(
                    name=content_name,
                    url=node.get('url'),
                    type=type_
                )

                if branch is not None:
                    content.branch = branch
                if parent is not None:
                    content.parent = parent
                content.save()

                if type_ == Content.DIRECTORY:
                    parse_tree(subtree[(i + 1):], level=(level + 1), parent=content)
                node['processed'] = True
            else:
                break
