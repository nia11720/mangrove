from core import Flask

app = Flask(__name__)
with app.app_context():
    from . import task
    from .blueprint import video, playlist, channel

    app.register_blueprint(video.bp, url_prefix="/video")
    app.register_blueprint(playlist.bp, url_prefix="/playlist")
    app.register_blueprint(channel.bp, url_prefix="/channel")
