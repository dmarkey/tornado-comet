from random import randint
import uuid

__author__ = 'dmarkey'
import tornado.httpclient
import tornado.ioloop
import json
headers = {'Content-Type': 'application/json; charset=UTF-8'}


def handle_request(response):
    if response.error:
        print "Error:", response.error
    else:
        print response.body


url = 'http://localhost:8080/pushback_lp/'
params = {'service': "diag_sdk"}



body = json.dumps(params)

for i in xrange(1, 1000):
    params['uuid'] = str(uuid.uuid4())
    body = json.dumps(params)
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_client.fetch(url, handle_request, method='POST', headers=headers,
                      body=body, request_timeout=6000, connect_timeout=300)

tornado.ioloop.IOLoop.instance().start()