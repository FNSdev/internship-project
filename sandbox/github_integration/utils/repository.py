import requests
import urllib.parse
from django.conf import settings
from github_integration.utils.decorators import safe_request


@safe_request
def _get_json_response_with_token(token, url):
    response = requests.get(
        url,
        headers={
            'Authorization': f'token {token}'
        }
    )

    return response.status_code, response.json()


def get_repository_list(token):
    url = '/'.join((settings.GITHUB_USER_URL, 'repos'))
    return _get_json_response_with_token(token, url)


def get_repository_info(token, user, repository):
    url = '/'.join((settings.GITHUB_REPOS_URL, user, repository))
    return _get_json_response_with_token(token, url)


def get_repository_branches(token, user, repository):
    url = '/'.join((settings.GITHUB_REPOS_URL, user, repository, 'branches'))
    return _get_json_response_with_token(token, url)


@safe_request
def _get_subdirectory_content(token, url):
    error, data = _get_json_response_with_token(token, url)
    if error is not None:
        return error, None

    content = []

    for d in data:
        if d.get('type') == 'file':
            content.append(d)
        elif d.get('type') == 'dir':
            error, data = _get_subdirectory_content(token, d.get('url'))

            if error is not None:
                return error, None

            d['content'] = data
            content.append(d)
        else:
            raise NotImplementedError(f'Content of type "{d.get("type")}" is not supported')

    return None, content


def get_repository_content(token, user, repository, branch):
    url = '/'.join((settings.GITHUB_REPOS_URL, user, repository, 'contents'))
    params = urllib.parse.urlencode({'ref': branch})
    url = f'{url}?{params}'
    return _get_subdirectory_content(token, url)
