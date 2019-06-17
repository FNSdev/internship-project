from github_integration.models import Content


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
