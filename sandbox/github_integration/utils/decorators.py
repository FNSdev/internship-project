from requests.exceptions import RequestException, ConnectionError, ConnectTimeout
from enum import Enum


class Errors(Enum):
    UNKNOWN_ERROR = 1
    CONNECTION_ERROR = 2
    CONNECTION_TIMEOUT = 3
    NOT_FOUND = 4
    NOT_ALLOWED = 5
    ERROR_IN_RESPONSE = 6


def safe_request(func):
    def new_func(*args, **kwargs):
        try:
            status_code, data = func(*args, **kwargs)
            if status_code == 401:
                return Errors.NOT_ALLOWED, None
            elif status_code == 404:
                return Errors.NOT_FOUND, None
            elif isinstance(data, dict) and data.get('error'):
                return Errors.ERROR_IN_RESPONSE, None
            return None, data
        except ConnectionError:
            return Errors.CONNECTION_ERROR, None
        except ConnectTimeout:
            return Errors.CONNECTION_TIMEOUT, None
        except RequestException:
            return Errors.UNKNOWN_ERROR, None

    return new_func
