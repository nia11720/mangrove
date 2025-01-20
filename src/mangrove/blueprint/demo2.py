from flask import Blueprint, request

from core.env import USER_AGENT

bp = Blueprint("demo2", __name__)


@bp.get("/")
def index():
    return "demo2"


@bp.get("/header")
def header():
    return dict(request.headers)


@bp.get("/user-agent")
def user_agent():
    return USER_AGENT


@bp.get("/referer")
def referer():
    return request.headers.get("Referer", "no-referer")
