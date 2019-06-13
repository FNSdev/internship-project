import requests
import urllib.parse
from requests.auth import HTTPBasicAuth
from github.config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_LOGIN_URL, \
    GITHUB_GET_TOKEN_URL, GITHUB_SCOPE, GITHUB_APPLICATIONS_URL


def get_login_url() -> str:
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'scope': GITHUB_SCOPE
    }
    params = urllib.parse.urlencode(params)
    return f'{GITHUB_LOGIN_URL}?{params}'


# TODO return error message
def create_token(code: str) -> str:
    response = requests.post(
        GITHUB_GET_TOKEN_URL,
        json={
            'code': code,
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET
        },
        headers={
            'Accept': 'application/json'
        }
    )
    if response.status_code == 200:
        response = response.json()
        if not response.get('error'):
            token = response.get('access_token')
            return token
    return None


def is_token_valid(token: str) -> bool:
    url = '/'.join((GITHUB_APPLICATIONS_URL, GITHUB_CLIENT_ID, 'tokens', token))
    response = requests.get(
        url,
        auth=HTTPBasicAuth(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)
    )

    return response.status_code == 200
