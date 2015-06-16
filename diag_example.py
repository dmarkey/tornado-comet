import time
from talk_back import Listener


class DiagSDKListener(Listener):
    service_name = "diag_sdk"

    def work(self, item):
        time.sleep(10)
        item.send_result("Thanks")


if __name__ == "__main__":

    DiagSDKListener().run()