from core import Flask

app = Flask("subapp2")


@app.get("/")
def index():
    return "subapp2"
