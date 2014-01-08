#-*- coding:utf-8 -*-

from gevent.queue import Queue
import json

from flask import Blueprint, Response
from flask import request, abort, jsonify

from utils import ServerSentEvent

subscriptions = []

# the array of led pixels
led_pixels = []

simu = Blueprint('simu', __name__)

@simu.route("/subscribe")
def log_subscribe():
    def gen():
        q = Queue()
        subscriptions.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            subscriptions.remove(q)

    return Response(gen(), mimetype="text/event-stream")

def send_data(dtype, data):
    """ Send data to the clients
    """
    output = {
        "dtype": dtype,
        "data": data
    }
    for sub in subscriptions[:]:
        sub.put(json.dumps(output))

@simu.route("/leds", methods=["GET"])
def set_leds():
    """ get leds color
    """
    return jsonify(led_pixels)

@simu.route("/leds",  methods=["PUT"])
def get_leds():
    """ Set leds color
    """
    if not request.headers['Content-Type'] == 'application/json':
        abort(415)
    data = request.json
    #XXX: validate the data !
    led_pixels = data
    send_data("leds", led_pixels)
    return jsonify({"msg":"ok"})

