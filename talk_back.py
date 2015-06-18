import json
import redis
import threading

redis_pub = redis.Redis()


class TalkBackRequest(object):
    def __init__(self, request, on_failure=None):
        self.request_data = request
        self.on_failure = on_failure

    def serialize(self):
        return json.dumps(self.request_data)



    def get_uuid(self):
        return self.request_data['uuid']

    def finish(self, result, status=200):
        wrapper = {'result_status': status, 'result_payload': result}
        success = redis_pub.publish("/pushback_outgoing/" +
                                    self.get_uuid(), json.dumps(wrapper))

        if not success and self.on_failure is not None:
            self.on_failure(wrapper)

    def unauthorized(self, message=None):
        self.finish(message, status=401)


class IncomingProcessor(object):
    service_name = None

    def deserialize(self, payload):
        return TalkBackRequest(request=json.loads(payload), on_failure=self.on_failure)

    def __init__(self):
        if not self.service_name:
            raise Exception("Please subclass and define service_name")
        self.redis = redis.Redis()
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe("/pushback_incoming/" + self.service_name)

    def on_failure(self, message):
        pass

    def process_incoming(self, item):
        try:
            incoming = json.loads(item)
        except TypeError:
            return

        request = TalkBackRequest(incoming, on_failure=self.on_failure)
        t = threading.Thread(target=self.work, args=(request, ))
        t.daemon = True
        t.start()

    def run(self):
        for item in self.pubsub.listen():
            if item['type'] == 'message':
                self.process_incoming(item['data'])










