from core import Flask

app = Flask(__name__)
with app.app_context():
    from .blueprint import video, playlist

    app.register_blueprint(video.bp, url_prefix="/video")
    app.register_blueprint(playlist.bp, url_prefix="/playlist")
