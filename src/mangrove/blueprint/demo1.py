from datetime import datetime

from flask import Blueprint

bp = Blueprint("demo1", __name__)


@bp.get("/text")
def text():
    return ["中文"]


@bp.get("/date")
def date():
    return [datetime.fromisoformat("2024-01-01 12:00:00")]
