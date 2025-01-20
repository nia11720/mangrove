from core import Flask

app = Flask("subapp")


@app.get("/")
def index():
    return "subapp"


with app.app_context():
    from .subapp2 import app as subapp2

    app.register_flask(subapp2, url_prefix="/subapp2")
