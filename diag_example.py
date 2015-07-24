from threading import Timer
import time
from talk_back import IncomingProcessor


requests = []

class DiagSDKProcessor(IncomingProcessor):
    service_name = "diag_sdk"

    def work(self, item):

        request_serialized = item.serialize()

        requests.append(request_serialized)


    def on_failure(self, message):
        print "Message failed to be delivered"



def emulate_push():
    print "Doing a push.."

    global requests

    for req in requests:

        item = DiagSDKProcessor().deserialize(req) # this can happen at any time on another process.
        results = {"Results": [{"Severity": "Low"}, {"Severity": "High"}, {"Severity": "Medium"}],
                   "original_request": item.request_data}  # included for illustration
        item.finish(results)
    requests = []

    Timer(30.0, emulate_push).start()


if __name__ == "__main__":

    Timer(30.0, emulate_push).start()

    DiagSDKProcessor().run()
