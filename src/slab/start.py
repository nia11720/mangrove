import gevent
from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()

from importlib import import_module
from signal import signal, SIGINT, SIGTERM, SIG_IGN, SIG_DFL
from logging import root, INFO, getLogger, Formatter, Handler, StreamHandler

import click

from core import huey, Redis


class RedisHandler(Handler):
    redis = Redis("log")

    def emit(self, record):
        try:
            msg = self.format(record)
            self.redis.lpush(record.name.replace(".", ":"), msg)
        except:
            self.handleError(record)


formatter = Formatter("{asctime} {levelname:>8} {name}: {message}", style="{")
formatter.default_msec_format = "%s.%03d"

stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)
redis_handler = RedisHandler()
redis_handler.setFormatter(formatter)


@click.command
@click.option("--host", "-h", default="localhost")
@click.option("--port", "-p", default=5000)
@click.option("--app", "-a", default="mangrove")
def main(host, port, app):
    root.setLevel(INFO)
    root.addHandler(stream_handler)
    root.addHandler(redis_handler)

    task = huey.create_consumer(workers=8, worker_type="gevent")
    task._set_signal_handlers = lambda: None

    wsgi = WSGIServer(
        (host, port),
        import_module(app).app,
        log=getLogger("wsgi.access"),
        error_log=getLogger("wsgi.error"),
    )

    def handle_stop(sig, frame):
        gevent.spawn(task.stop, graceful=True)
        gevent.spawn(wsgi.stop)
        signal(SIGINT, SIG_DFL)
        signal(SIGTERM, SIG_DFL)

    signal(SIGINT, handle_stop)
    signal(SIGTERM, handle_stop)

    task.start()
    wsgi.start()
    gevent.wait()


if __name__ == "__main__":
    main()
