from flask import current_app

from core import Redis

redis = Redis(current_app.name)
