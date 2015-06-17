import time
from talk_back import Listener


class DiagSDKListener(Listener):
    service_name = "diag_sdk"

    def work(self, item):
        time.sleep(10)
        item.unauthorized("Not authorized")

    def on_failure(self, message):
        print "Message failed"

if __name__ == "__main__":

    DiagSDKListener().run()