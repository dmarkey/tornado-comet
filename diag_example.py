import time
from talk_back import IncomingProcessor


class DiagSDKProcessor(IncomingProcessor):
    service_name = "diag_sdk"

    def work(self, item):

        request_serialized = item.serialize()
        #Emulate serialising the request to database etc
        #time.sleep(10)
        #Emulate some diag activity...

        new_request = self.deserialize(request_serialized) # this can happen at any time on another process.
        results = {"Results": [{"Severity": "Low"}, {"Severity": "High"}, {"Severity": "Medium"}],
                   "original_request": item.request_data}  # included for illustration
        new_request.finish(results)

    def on_failure(self, message):
        print "Message failed to be delivered"

if __name__ == "__main__":

    DiagSDKProcessor().run()