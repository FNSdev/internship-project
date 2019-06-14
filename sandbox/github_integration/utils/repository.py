import requests
from django.conf import settings
from github_integration.utils.decorators import safe_request


@safe_request
def get_repository_list(token):
    url = '/'.join((settings.GITHUB_USER_URL, 'repos'))

    response = requests.get(
        url,
        headers={
            'Authorization': f'token {token}'
        }
    )

    return response.status_code, response.json()


@safe_request
def get_repository_info(token, user, repository):
    url = '/'.join((settings.GITHUB_REPOS_URL, user, repository))

    response = requests.get(
        url,
        headers={
            'Authorization': f'token {token}'
        }
    )

    return response.status_code, response.json()


@safe_request
def get_repository_branches(token, user, repository):
    url = '/'.join((settings.GITHUB_REPOS_URL, user, repository, 'branches'))
    response = requests.get(
        url,
        headers={
            'Authorization': f'token {token}'
        }
    )

    return response.status_code, response.json()


def get_repository_content(token, user, name):
    pass
