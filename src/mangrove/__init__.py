from core import Flask

app = Flask(__name__)

with app.app_context():
    import bilibili
    import youtube
    from .blueprint import test, cpolar

    app.register_flask(bilibili.app, url_prefix="/b")
    app.register_flask(youtube.app, url_prefix="/ytb")

    app.register_blueprint(test.bp, url_prefix="/test")
    app.register_blueprint(cpolar.bp, url_prefix="/cpolar")


@app.get("/")
def index():
    return __name__
