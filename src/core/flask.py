from datetime import datetime

from flask import Flask as _Flask
from flask.json.provider import DefaultJSONProvider
from werkzeug.middleware.dispatcher import DispatcherMiddleware


class JSONProvider(DefaultJSONProvider):
    ensure_ascii = False

    @staticmethod
    def default(obj):
        if isinstance(obj, datetime):
            return f"{obj.astimezone()}"
        else:
            return super(__class__, __class__).default(obj)


class Flask(_Flask):
    json_provider_class = JSONProvider

    def __init__(self, import_name: str):
        super().__init__(import_name, static_folder=None, template_folder=None)
        self.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 8
        self.wsgi_app = DispatcherMiddleware(super().wsgi_app)

    def register_flask(self, app: _Flask, url_prefix: str):
        app.config["APPLICATION_ROOT"] = url_prefix
        self.wsgi_app.mounts[url_prefix] = app
