#-*- coding:utf-8 -*-
import time
import datetime
import redis
from gevent.pool import Pool
from gevent import monkey
import threading
import settings
from package_loader import load_package
from redis_queue import Queue
monkey.patch_all()

class Task(object):
    '''scheduler: pull project script, pull queue data, call the script function to process data'''
    def __init__(self, project_name):
        self.status_channel = '%s_status' %project_name
        self.stop_flag = 0
        self.dead_time = 0
        self.status = 'waiting'
        self.update_timestamp()
        t = threading.Thread(target = self.dead_time_counter)
        t.start()

    def load_package(self, package_name):
        Consumer = load_package(package_name)
        self.consumer = Consumer()
        self.queue = Queue(self.consumer.redis_client, self.consumer.redis_key)

    def update_timestamp(self):
        '''record the time when the task status is updated'''
        self.t = datetime.datetime.now()

    def dead_time_counter(self):
        '''monitor whether the task is dead'''
        while True:
            self.dead_time += 1
            time.sleep(1)

    def start(self, package_name=None, worknum=1, sleep_interval=0, queue_num=1, pull_size=100):
        '''slow mode: worknum=1, sleep_interval=N
                    every worker is blocking, sleep N seconds;
           fast mode: worknum=N
                    every worker is non-blocking, using gevent concurrent 
                    pool
           queue_num: number of queues. redis queue is slow when queue size > 100000, so a list of queues is needed for big data.
           pull_size: pull N items for consumer.
           '''
        try:
            self.load_package(package_name)
        except Exception as e:
            logging.error(e)
        self.status = 'running'
        self.update_timestamp()
        self.stop_flag = 0
        self.queue.config_params(queue_num, pull_size)
        if worknum == 1: #慢速模式
            self.start_single_worker(sleep_interval)
        else: #快速模式
            self.start_concurrent_worker(worknum)
        self.status = 'finished'
        self.update_timestamp()

    def start_single_worker(self, sleep_interval):
        '''slow mode,every worker is blocking'''
        total_count = 0
        while True:
            self.dead_time = 0
            items = self.queue.pull()
            if not items:
                break
            for item in items:
                if not item:
                    continue
                self.work(item)
                if sleep_interval:
                    time.sleep(sleep_interval)
                total_count += 1
            self.status = '%d updated' %total_count
            self.update_timestamp()
            if self.stop_flag:
                break

    def start_concurrent_worker(self, worknum):
        '''fast mode: every worker is non-blocking, using gevent concurrent Pool'''
        total_count = 0
        g = Pool(worknum) 
        while True:
            self.dead_time = 0
            items = self.queue.pull()
            if not items:
                break
            for item in items:
                if not item:
                    continue
                g.spawn(self.work, item)
                total_count += 1
            self.status = '%d updated' %total_count
            self.update_timestamp()
            g.join()
            if self.stop_flag:
                break
        g.join()

    def work(self, item):
        '''call the loaded script to process item'''
        item = item.decode() #for python3
        data = self.consumer.worker(item)
        self.consumer.pipeline(item, data)
        self.dead_time = 0

    def stop(self):
        '''stop the task lazily'''
        self.stop_flag = 1
        self.status = 'stopped'
        self.update_timestamp()

    def state(self):
        '''send task status to redis server'''
        status_string = "%s, %s, %s" %(self.status, self.dead_time, self.t)
        status_db = redis.StrictRedis(**settings.redis_status_conf)
        status_db.hset(self.status_channel, Runtime().local_ip, status_string)

    def is_idle(self):
        return self.status in ['waiting','stopped','finished'] or self.dead_time > 120

    def is_dead(self):
        return self.dead_time > 1000
