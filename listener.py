from tornado import websocket

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

publisher = tornadoredis.Client()

client = tornadoredis.Client()

SERVICES = ['diag_sdk', "upload_tricklefeed"]


class CISSubscriber(tornadoredis.pubsub.BaseSubscriber):
    """
    Use this class to send messages from the redis channel directly to
    subscribers via SocketIO connection (thanks to Ofir Herzas)
    """
    def on_message(self, msg):
        if not msg:
            return
        if msg.kind == 'message' and msg.body:
            # Get the list of subscribers for this channel
            subscribers = list(self.subscribers[msg.channel].keys())
            if subscribers:
                for subscriber in subscribers:
                    subscriber.on_redis_message(msg.body)
        super(CISSubscriber, self).on_message(msg)


subscriber = CISSubscriber(tornadoredis.Client())


class MixIn(object):

    def check_request(self, message):
        self.pubsub_topic = None
        print(message)
        try:
            data = json.loads(message)
            #my_uuid = hashlib.sha224(message).hexdigest()
            my_uuid = data['uuid']
        except ValueError:
            self.set_status(400)
            self.finish("Error parsing JSON")
            return False

        service = data.get("service", "")

        if service not in SERVICES:
            self.set_status(400)
            self.finish("Invalid service " + service)
            return False

        print(my_uuid)
        self.pubsub_topic = "/pushback_outgoing/" + my_uuid
        data['uuid'] = my_uuid
        self.data = data
        self.service = service
        logging.error(self.pubsub_topic)

        self.subscriber = CISSubscriber(client)
        self.subscriber.subscribe(self.pubsub_topic, self, callback=self.on_sub)

    def on_sub(self, success):
        if success:
            publisher.publish("/pushback_incoming/" + self.service, json.dumps(self.data))
        else:
            print "Fail"

    def done(self):
        return
        if self.pubsub_topic:
            self.client.disconnect()
            self.pubsub_topic = None


class WSHandler(websocket.WebSocketHandler, MixIn):

    def check_origin(self, origin):
        return True

    def set_status(self, status_code, reason=None):
        pass

    def finish(self, chunk=None):
        self.write_message(chunk)
        self.close()

    def on_redis_message(self, result):
        result_obj = json.loads(result)
        self.set_status(result_obj['result_status'])
        self.write_message(result_obj['result_payload'])

    def on_message(self, message):
        self.check_request(message)

    def on_close(self):
        self.done()



class LongPollHandler(RequestHandler, MixIn):

    @asynchronous
    def post(self):
        self.check_request(self.request.body)

    def on_redis_message(self, result):
        result_obj = json.loads(result)
        self.set_status(result_obj['result_status'])
        self.finish(result_obj['result_payload'])
        self.done()

    def on_finish(self):
        self.done()

    def on_connection_close(self):
        self.done()


application = tornado.web.Application([
    (r'/pushback_ws/', WSHandler),
    (r"/pushback_lp/", LongPollHandler),
])

if __name__ == "__main__":
    application.listen(8080)
    from tornado.log import enable_pretty_logging
    from tornado.options import options
    options.log_to_stderr = True
    enable_pretty_logging(options=options)
    tornado.ioloop.IOLoop.instance().start()
