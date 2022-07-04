from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

import pytest

from testapp import urls  # noqa


def dummy_get_response(request):
    raise NotImplementedError()


@pytest.fixture()
def request_with_middleware(rf):
    request = rf.get("/")
    SessionMiddleware(get_response=dummy_get_response).process_request(request)
    MessageMiddleware(get_response=dummy_get_response).process_request(request)
    return request
