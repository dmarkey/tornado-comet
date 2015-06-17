__author__ = 'dmarkey'
import json
import hashlib
import tornadoredis.pubsub
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler, asynchronous
import logging
logging.basicConfig(filename="logfile.txt")
logging.getLogger().addHandler(logging.StreamHandler())
subscriber = tornadoredis.pubsub.SocketIOSubscriber(tornadoredis.Client())
publisher = tornadoredis.Client()

SERVICES = ['diag_sdk', "upload_tricklefeed"]


class Handler(RequestHandler):

    @asynchronous
    def post(self):
        self.pubsub_topic = None

        try:
            data = json.loads(self.request.body)
            my_uuid = hashlib.sha224(self.request.body).hexdigest()
        except ValueError:
            self.set_status(400)
            self.finish("Error parsing JSON")
            return

        service = data.get("service", "")

        if service not in SERVICES:
            self.set_status(400)
            self.finish("Invalid service " + service)
            return

        self.pubsub_topic = "/pushback_outgoing/" + my_uuid
        data['uuid'] = my_uuid
        self.data = data
        self.service = service
        logging.error(self.pubsub_topic)
        subscriber.subscribe(self.pubsub_topic, self, callback=self.on_sub)

    def on_sub(self, success):
        if success:
            publisher.publish("/pushback_incoming/" + self.service, json.dumps(self.data))

    def on_message(self, result):
        result_obj = json.loads(result)
        self.set_status(result_obj['result_status'])
        self.finish(result_obj['result_payload'])

    def on_finish(self):
        if self.pubsub_topic:
            subscriber.unsubscribe(self.pubsub_topic, self)

    def on_connection_close(self):
        if self.pubsub_topic:
            subscriber.unsubscribe(self.pubsub_topic, self)


application = tornado.web.Application([
    (r"/pushback/", Handler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
