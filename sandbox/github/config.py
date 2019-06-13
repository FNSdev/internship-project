import os


GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GITHUB_SCOPE = 'repo user'

GITHUB_LOGIN_URL = 'https://github.com/login/oauth/authorize'
GITHUB_GET_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_APPLICATIONS_URL = 'https://api.github.com/applications'
