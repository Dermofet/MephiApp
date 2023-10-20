from fastapi import Request
from user_agents import parse


def get_user_os(request: Request):
    user_agent = parse(request.headers.get("User-Agent"))
    return user_agent.os.family
