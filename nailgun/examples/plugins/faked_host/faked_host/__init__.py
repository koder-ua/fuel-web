import time
import urllib2
import requests
from threading import Lock

from nailgun.plugin_interface import INGBackgroundTask


doc = """
"""

class FakedHost(INGBackgroundTask):
    
    url = "http://localhost:8000/api/nodes"
    def run(self):
        time.sleep(5)
        while True:
            t = time.time()
            request = urllib2.Request(url, 
                                      data=data_json,
                                      headers=self.headers)
            if data_json is not None:
                request.add_header('Content-Type', 'application/json')

            request.get_method = lambda: method.upper()
            responce = urllib2.urlopen(request)

            if responce.code < 200 or responce.code > 209:
                raise IndexError(url)

            content = responce.read()
            requests.post(url, doc)
            stime = t + 60 - time.time()
            if stime > 0:
                time.sleep(stime)

    def stop(self):
        pass
