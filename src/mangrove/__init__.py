from core import Flask

app = Flask(__name__)

with app.app_context():
    import bilibili
    from .blueprint import test

    app.register_flask(bilibili.app, url_prefix="/b")

    app.register_blueprint(test.bp, url_prefix="/test")


@app.get("/")
def index():
    return __name__
