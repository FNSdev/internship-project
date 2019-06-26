import requests
import urllib.parse
from django.conf import settings
from github_integration.utils.decorators import safe_request


@safe_request
def _get_json_response_with_token(token, url):
    """Adds token to request headers"""

    response = requests.get(
        url,
        headers={
            'Authorization': f'token {token}'
        }
    )

    return response.status_code, response.json()


def get_repository_list(token):
    """Returns all repositories that user own's"""

    url = '/'.join((settings.GITHUB_USER_URL, 'repos'))
    params = {
        'type': 'owner',
    }
    params = urllib.parse.urlencode(params)
    url = f'{url}?{params}'
    return _get_json_response_with_token(token, url)


def get_repository_info(token, user, repository):
    """Returns repository details"""

    url = '/'.join((settings.GITHUB_REPOS_URL, user, repository))
    return _get_json_response_with_token(token, url)


def get_repository_branches(token, user, repository):
    """Return repository branches"""

    url = '/'.join((settings.GITHUB_REPOS_URL, user, repository, 'branches'))
    return _get_json_response_with_token(token, url)


def get_repository_tree(token, user, repository, sha):
    """Recursively gets repository tree"""

    url = '/'.join((settings.GITHUB_REPOS_URL, user, repository, 'git', 'trees', sha))
    params = {
        'recursive': 1,
    }
    params = urllib.parse.urlencode(params)
    url = f'{url}?{params}'
    return _get_json_response_with_token(token, url)


def get_blob(token, url):
    """Returns an object used to store contents of file on GitHub"""

    return _get_json_response_with_token(token, url)
