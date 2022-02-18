#-*- coding:utf-8 -*-
import random
import time
import logging
class Queue(object):
    '''A FIFO queue from a redis list'''
    def __init__(self, redis_client, redis_key):
        self.redis_client = redis_client
        self.redis_key = redis_key
        self.queue_num = 1
        self.pull_size = 100

    def config_params(self, queue_num=None, pull_size=None):
        if queue_num:
            self.queue_num = queue_num
        if pull_size:
            self.pull_size = pull_size

    def pull(self):
        if self.queue_num == 1:
            return self._pull_single_queue()
        else:
            return self._pull_multi_queue(depth=0)

    def push_items(self, generator, push_size=10000):
        if self.queue_num == 1:
            self._push_single_queue(generator, push_size)
        else:
            self._push_multi_queue(generator, push_size)

    def push(self, item):
        self.redis_client.rpush(self.redis_key, item)


    def _pull_single_queue(self):
        items = get_items(self.redis_client, self.redis_key, self.pull_size)
        if all([x is None for x in items]):
            return None
        return items

    def _pull_multi_queue(self, depth):
        depth += 1
        if depth == 100: #limit the depth of recursion
            return None
        sequence = random.randint(0, self.queue_num)
        redis_key = '%s:%s' %(self.redis_key, sequence)
        items = get_items(self.redis_client, redis_key, self.pull_size)
        if all([x is None for x in items]):
            return self._pull_multi_queue(depth)
        return items

    def _push_single_queue(self, generator, push_size):
        put_items(self.redis_client, self.redis_key, generator, push_size)

    def _push_multi_queue(self, generator, push_size):
        put_items_to_multi_seq(self.redis_client, self.redis_key,  \
                             generator, self.queue_num, push_size)

def network_safety():
    def wrap(func):
        def wrapper(*args):
            while True:
                try:
                    return func(*args)
                except Exception as e:
                    logging.warn('redis block %s' %str(e))
                    time.sleep(2)
                    continue
        return wrapper
    return wrap

@network_safety()
def get_items(redis_client, redis_key, pull_size=100):
    '''lpop(redis_key) N times is faster than lpop(redis_key, N)'''
    pipe = redis_client.pipeline()
    for _ in range(pull_size):
        pipe.lpop(redis_key)
    return pipe.execute()

@network_safety()
def put_items(redis_client, redis_key, generator, push_size=10000):
    i = 0
    pipe = redis_client.pipeline()
    for item in generator:
        i += 1
        pipe.rpush(redis_key, item)
        if i % push_size == 0:
            pipe.execute()
    pipe.execute()

@network_safety()
def put_items_to_multi_seq(redis_client, redis_key, generator, \
                           queue_num, push_size=10000):
    i = 0
    pipe = redis_client.pipeline()
    for item in generator:
        i += 1
        redis_key_i = '%s:%s' %(redis_key, i % queue_num) 
        pipe.rpush(redis_key_i, item)
        if i % push_size == 0:
            pipe.execute()
    pipe.execute()

