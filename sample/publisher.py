#-*- coding:utf8 -*-
import sys
sys.path.append('../')
import redis
import logging
import json
import settings
class Publisher(object):
    def __init__(self):
        self.redis_client = redis.StrictRedis(**settings.redis_control_conf)

    def publish(self, data):
        serial_data = json.dumps(data)
        self.redis_client.publish(settings.redis_control_channel, serial_data)
        logging.info(serial_data)

    def start(self, project_name, worknum=3, sleep_interval=0, queue_num=1, pull_size=100, ips=None):
        '''slow mode: worknum=1, sleep_interval=N
                    every worker is blocking, sleep N seconds;
           fast mode: worknum=N
                    every worker is non-blocking, using gevent concurrent pool
           queue_num: number of queues. redis queue is slow when queue size > 100000, 
                      so a list of queues is needed for big data.
           pull_size: pull N items for consumer.
           ips: assign work nodes. default is None, assign all subscribers.
           '''
        action = 'restart'
        data = {'project': project_name,
                'action': action, 
                'worknum': worknum,
                'sleep_interval': sleep_interval, 
                'queue_num': queue_num, 
                'pull_size': pull_size,
                'ips': ips}
        self.publish(data)

    def stop(self, project_name):
        action = 'stop'
        data = {'project': project_name,'action': action}
        self.publish(data)

    def status(self, project_name):
        action = 'status'
        data = {'project': project_name,'action': action}
        self.publish(data)
