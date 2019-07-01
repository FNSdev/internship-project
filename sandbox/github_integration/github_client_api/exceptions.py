class GitHubApiRequestException(Exception):
    """Basic GitHub API Request Exception"""

    message = 'REQUEST EXCEPTION'

    def __init__(self, request_url=None):
        self.request_url = request_url


class GitHubApiNotFound(GitHubApiRequestException):
    """HTTP 404 response status"""
    message = "NOT FOUND"


class GitHubApiAccessDenied(GitHubApiRequestException):
    """HTTP 403 response status"""
    message = "ACCESS DENIED"


class GitHubApiConnectionError(GitHubApiRequestException):
    """GitHub API connection error"""
    message = "CONNECTION ERROR"


class GitHubApiTimeout(GitHubApiRequestException):
    """GitHub API timeout"""
    message = "TIMEOUT"


class GitHubApiHTTPError(GitHubApiRequestException):
    """GitHub API HTTP Error"""
    message = "HTTP ERROR"


class GitHubApiErrorInResponse(GitHubApiRequestException):
    """Request was successful, but there is an error in response message"""
    message = "ERROR IN RESPONSE"
