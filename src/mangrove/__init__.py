from core import Flask

app = Flask(__name__)


@app.get("/")
def index():
    return "mangrove"


with app.app_context():
    from .subapp import app as subapp
    from .blueprint import demo1

    app.register_flask(subapp, url_prefix="/subapp")
    app.register_blueprint(demo1.bp, url_prefix="/demo1")
