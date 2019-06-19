import requests
import urllib.parse
from requests.auth import HTTPBasicAuth
from django.conf import settings
from github_integration.utils.decorators import safe_request


def get_login_url() -> str:
    params = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'scope': settings.GITHUB_SCOPE
    }
    params = urllib.parse.urlencode(params)
    return f'{settings.GITHUB_LOGIN_URL}?{params}'


@safe_request
def get_username(token: str):
    response = requests.get(
        settings.GITHUB_USER_URL,
        headers={
            'Authorization': f'token {token}',
        }
    )
    return response.status_code, response.json().get('login')


@safe_request
def create_token(code: str):
    response = requests.post(
        settings.GITHUB_GET_TOKEN_URL,
        json={
            'code': code,
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET
        },
        headers={
            'Accept': 'application/json'
        }
    )

    return response.status_code, response.json().get('access_token')


@safe_request
def is_token_valid(token: str) -> bool:
    url = '/'.join((settings.GITHUB_APPLICATIONS_URL, settings.GITHUB_CLIENT_ID, 'tokens', token))
    response = requests.get(
        url,
        auth=HTTPBasicAuth(settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
    )

    return response.status_code, response.status_code == 200
