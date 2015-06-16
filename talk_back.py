import json
import redis
import threading
import time

redis_pub = redis.Redis()





class TalkBackResult(object):

    def __init__(self, request):
        self.request = request

    def finish(self, result):
        redis_pub.publish("/pushback_outgoing/" + self.request.get_uuid(), result)


class TalkBackRequest(object):

    def __init__(self, request):
        self.request_data = request

    def get_uuid(self):
        return self.request_data['uuid']

    def send_result(self, payload):
        TalkBackResult(self).finish(payload)


class Listener(threading.Thread):

    service_name = None

    def __init__(self):
        if not self.service_name:
            raise Exception("Please subclass and define service")
        threading.Thread.__init__(self)
        self.redis = redis.Redis()
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("/pushback_incoming/" + self.service_name)


    def process_incoming(self, item):
        print item
        try:
            incoming = json.loads(item)
        except TypeError:
            return

        request = TalkBackRequest(incoming)

        self.work(request)

    def run(self):
        for item in self.pubsub.listen():
            if item['type'] == 'message':
                self.process_incoming(item['data'])










