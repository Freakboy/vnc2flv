#!/usr/bin/env python


from flask import Response, json, request, current_app, Blueprint
from .recorder import RecorderActiveError

routes = Blueprint(__name__, __name__)


@routes.route("/recording", methods=['POST'])
def start_recording():
    try:
        ins = {}
        config_from_request = request.get_json()
        if config_from_request is not None:
            # config.update(config_from_request)
            ins = config_from_request
            print('ins', ins)
            current_app.recorder.start(ins)
    except RecorderActiveError:

        return Response(
            json.dumps({'success': False, "message": "already recording"}),
            status=409,
            mimetype='application/json'
        )

    return Response(
        json.dumps({'success': True}),
        status=201,
        mimetype='application/json'
    )


@routes.route("/recording", methods=['DELETE'])
def stop_recording():
    current_app.recorder.stop()
    return Response(
        json.dumps({'success': True}),
        status=200,
        mimetype='application/json'
    )


@routes.route("/recording", methods=['GET'])
def show_status():
    return json.jsonify(current_app.recorder.get_status())
