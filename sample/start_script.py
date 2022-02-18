#-*- coding:utf-8 -*-
import sys
sys.path.append('../')
import logging
import os
import redis
from ftp_script_server import ftp_upload_dir
from consumer import Consumer
from db_backend import PostgresqlBackend
from redis_queue import Queue
from publisher import Publisher
import settings
import json
package_path = os.getcwd()
project_name = os.path.basename(package_path)
logfile_name = os.path.join(settings.logfile_dir, '%s.log' %project_name)
logging.basicConfig(filename=logfile_name, level=logging.ERROR,  \
                 format = '%(asctime)s - %(levelname)s: %(message)s')
redis_conf = {
    'host': '127.0.0.1',
    'port': 7000,
    'db': 0,
    'password': 'xxx'
        }
redis_client = redis.StrictRedis(**redis_conf)
redis_key = project_name
postgres_conf = {
    'host': '127.0.0.1',
    'user': 'postgres',
    'password' : 'xxx',
    'dbname': 'test',
        }
data_table = 'test'

class MyConsumer(Consumer):
    name = project_name
    a = 2
    def __init__(self):
        super(MyConsumer, self).__init__()
        self.data_backend = PostgresqlBackend(**postgres_conf)
        self.redis_client = redis.StrictRedis(**redis_conf)
        self.redis_key = redis_key

    def url_factory(self, item):
        return item

    def download(self, item):
        return item

    def parse(self, recv):
        return json.dumps({'recv': recv})

    def write_data(self, item, data):
        self.data_backend.insert(data_table, item, data)

def read_input(input_file):
    with open(input_file,'r') as fin:
        for line in fin:
            line = line.strip()
            yield line

def data_to_queue(input_file, queue_num=1):
    generator = read_input(input_file)
    queue = Queue(redis_client, redis_key)
    queue.config_params(queue_num=queue_num)
    queue.push_items(generator)

def test_worker():
    for item in read_input('./input.txt'):
        print(MyConsumer().worker(item))
        break

def upload_script():
    ftp_upload_dir(project_name)

if __name__ == '__main__':
    upload_script()
    queue_num = 2
    data_to_queue('./input.txt', queue_num = queue_num)
    Publisher().start(project_name, worknum=3,  \
                 queue_num=queue_num, pull_size=2)

