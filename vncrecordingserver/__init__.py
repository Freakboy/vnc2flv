#!/usr/bin/env python
from flask import Flask
# from .recorder import Recorder
from vncrecordingserver.tt2 import Recorder
# from .server import routes
from vncrecordingserver.ser_2 import routes

__version__ = '1.0.0'


def create_app():
    """Returns a :class:`Flask` application instance configured with common
    functionality for the application

    :param config: recorder function
    :return:
    """
    app = Flask(__name__)
    app.recorder = Recorder()
    app.register_blueprint(routes)

    return app


def run():
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
