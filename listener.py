import json

__author__ = 'dmarkey'
import tornadoredis.pubsub
subscriber = tornadoredis.pubsub.SocketIOSubscriber(tornadoredis.Client())
publisher = tornadoredis.Client()
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler, Application, asynchronous
import uuid
SERVICES = ['diag_sdk', "upload_tricklefeed"]

import logging
logging.basicConfig(filename="logfile.txt")
logging.getLogger().addHandler(logging.StreamHandler())


class Handler(RequestHandler):

    @asynchronous
    def post(self):
        print(self);

        self.pubsub_topic = None

        try:
            data = json.loads(self.request.body)
        except ValueError:
            self.set_status(400)
            self.finish("Error parsing JSON")
            return

        service = data.get("service", "")

        if service not in SERVICES:
            self.set_status(400)
            self.finish("Invalid service " + service)
            return

        my_uuid = str(uuid.uuid4())
        self.pubsub_topic = "/pushback_outgoing/" + my_uuid
        data['uuid'] = my_uuid
        self.data = data
        self.service = service
        logging.error(self.pubsub_topic)
        subscriber.subscribe(self.pubsub_topic, self, callback=self.on_sub)

    def on_sub(self, success):
        print success
        if success:
            publisher.publish("/pushback_incoming/" + self.service, json.dumps(self.data))

    def on_message(self, msg):
        """ New message, close out connection. """
        self.finish({"message": msg})

    def on_finish(self):
        if self.pubsub_topic:
            subscriber.unsubscribe(self.pubsub_topic, self)


application = tornado.web.Application([
    #(r"/publish/(.*)", GetGameByIdHandler),
    (r"/pushback/", Handler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
