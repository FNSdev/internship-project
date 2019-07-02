import requests
import urllib.parse
from django.conf import settings
from functools import wraps
from github_integration.github_client_api.exceptions import (
    GitHubApiRequestException,
    GitHubApiAccessDenied,
    GitHubApiNotFound,
    GitHubApiTimeout,
    GitHubApiConnectionError,
    GitHubApiHTTPError,
    GitHubApiErrorInResponse,
)
from requests.auth import HTTPBasicAuth
from requests.exceptions import (
    HTTPError,
    ConnectionError,
    Timeout,
    RequestException
)


def _github_api_request(func):
    """Requires (response_status_code, data, url) to be returned from func"""

    @wraps(func)
    def new_func(*args, **kwargs):
        url = None
        try:
            response_status_code, data, url = func(*args, **kwargs)
            if response_status_code == 403 or (isinstance(data, dict) and data.get('message') == 'Bad credentials'):
                raise GitHubApiAccessDenied(request_url=url)
            elif response_status_code == 404:
                raise GitHubApiNotFound(request_url=url)
            elif isinstance(data, dict) and data.get('error'):
                raise GitHubApiErrorInResponse(request_url=url)
            else:
                return data
        except Timeout:
            raise GitHubApiTimeout(request_url=url)
        except ConnectionError:
            raise GitHubApiConnectionError(request_url=url)
        except HTTPError:
            raise GitHubApiHTTPError(request_url=url)
        except RequestException:
            raise GitHubApiRequestException(request_url=url)

    return new_func


class GitHubClient:
    """Provides methods to work with GitHub API"""

    # 1 MB
    MAX_RESPONSE_SIZE = 1_048_576

    # 5 seconds
    TIMEOUT = 5

    # 16 KB
    CHUNK_SIZE = 16384

    def __init__(self, token):
        self._token = token

    @staticmethod
    def make_url(*args, **kwargs):
        url = '/'.join(args)
        params = urllib.parse.urlencode(kwargs)
        return f'{url}?{params}'

    @staticmethod
    def get_github_login_url() -> str:
        """Returns GitHub login url for this application"""

        params = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'scope': settings.GITHUB_SCOPE
        }
        params = urllib.parse.urlencode(params)
        return f'{settings.GITHUB_LOGIN_URL}?{params}'

    @_github_api_request
    def get_json_response_with_token(self, url):
        """Adds token to request headers and makes sure that response is not larger than specified"""

        response = requests.get(
            url,
            headers={
                'Authorization': f'token {self._token}'
            },
            # stream=True,
        )

        # TODO check response size
        """content = ''
        for chunk in response.iter_content(self.CHUNK_SIZE):
            content += chunk
            if len(content) > self.MAX_RESPONSE_SIZE:
                response.close()
                return (
                    response.status_code,
                    {'error': f'Response is larger than {self.MAX_RESPONSE_SIZE} bytes'},
                    url
                )"""

        return response.status_code, response.json(), url

    @_github_api_request
    def create_token(self, code):
        """Creates GitHub OAuth token. Code from GitHub login callback is required"""

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

        return (
            response.status_code,
            response.json(),
            settings.GITHUB_GET_TOKEN_URL
        )

    @_github_api_request
    def is_token_valid(self):
        """Checks if user's GitHub token is valid. If it's not, response status code will be 404"""

        url = '/'.join((settings.GITHUB_APPLICATIONS_URL, settings.GITHUB_CLIENT_ID, 'tokens', self._token))
        response = requests.get(
            url,
            auth=HTTPBasicAuth(settings.GITHUB_CLIENT_ID, settings.GITHUB_CLIENT_SECRET)
        )

        return (
            response.status_code,
            response.status_code == 200,
            url
        )

    def get_username(self):
        """Return user GitHub username"""

        return self.get_json_response_with_token(settings.GITHUB_USER_URL)

    def get_repository_list(self):
        """Returns all repositories that user own's"""

        url = GitHubClient.make_url(
            settings.GITHUB_USER_URL,
            'repos',
            type='owner'
        )

        return self.get_json_response_with_token(url)

    def get_repository_info(self, user, repository):
        """Returns repository details"""

        url = GitHubClient.make_url(settings.GITHUB_REPOS_URL, user, repository)
        return self.get_json_response_with_token(url)

    def get_repository_branches(self, user, repository):
        """Return repository branches"""

        url = GitHubClient.make_url(settings.GITHUB_REPOS_URL, user, repository, 'branches')
        return self.get_json_response_with_token(url)

    def get_repository_tree(self, user, repository, sha):
        """Recursively gets repository tree"""

        url = GitHubClient.make_url(
            settings.GITHUB_REPOS_URL,
            user,
            repository,
            'git',
            'trees',
            sha,
            recursive=1
        )

        return self.get_json_response_with_token(url)

    # TODO check response size
    def get_blob(self, url):
        """Returns an object used to store contents of file on GitHub"""

        return self.get_json_response_with_token(url)
