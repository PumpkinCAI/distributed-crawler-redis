#-*- coding:utf-8 -*-
import gevent
import requests
import logging
from redis_queue import Queue
class Timeout(Exception):
    pass 

class Consumer(object):
    def __init__(self):
        self.data_backend = None
        self.redis_client = None
        self.redis_key = None

    def download(self, url):
        for _ in range(10):
            try:
                with gevent.Timeout(120, Timeout):
                    recv = requests.get(url).text
                    return recv
            except Timeout:
                logging.warn('timeout')
                gevent.sleep(2)
            except Exception:
                logging.error('download error')
                gevent.sleep(2)
        return None

    def worker(self, item):
        url = self.url_factory(item)
        recv = self.download(url)
        if not recv:
            self._push_back(item)
            return -1
        try:
            data = self.parse(recv)
        except Exception as e:
            logging.error('parse data error %s' %str(e))
            self._push_back(item)
            return -1
        return data

    def url_factory(self, item):
        pass

    def parse(self, recv):
        pass

    def write_data(self, item, data):
        pass

    def pipeline(self, item, data):
        if data == -1:
            return
        self.write_data(item, data)

    def push(self, item):
        Queue(self.redis_client, self.redis_key).push(item)

    def _push_back(self, item):
        self.push(item)

