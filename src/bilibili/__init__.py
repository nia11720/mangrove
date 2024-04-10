from core import Flask

app = Flask(__name__)
with app.app_context():
    from .blueprint import auth, video

    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(video.bp, url_prefix="/video")
