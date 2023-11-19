from fastapi import Request

from utils.version import Version


def get_version(request: Request) -> Version:
    return request.headers.get("X-API-VERSION", "0.0.1")
