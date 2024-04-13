from smtplib import SMTP
from email.message import EmailMessage

from flask import Blueprint

from core import huey
from mangrove.extensions import redis

bp = Blueprint("cpolar", __name__)


@bp.get("/")
def index():
    url = redis.get("@cpolar:top")
    return f'<a href="{url}" target="_blank">{url}</a>'


@huey.task()
def notify(text):
    host, port = ("smtp-mail.outlook.com", 587)
    username, password = redis.hmget("outlook", "username", "password")

    msg = EmailMessage()
    msg["From"] = username
    msg["To"] = username
    msg["Subject"] = "Notification"
    msg.set_content(text)

    with SMTP(host, port) as con:
        con.starttls()
        con.login(username, password)
        con.send_message(msg)


@huey.periodic_task("20 *")
def check():
    url, notified_url = redis.mget("@cpolar:top", "cpolar.notified_url")

    if notified_url != url:
        redis.set("cpolar.notified_url", url)
        notify(url)
