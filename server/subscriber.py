#-*- coding:utf-8 -*-
import sys
sys.path.append('..')
import redis 
import json
import datetime
import gevent
import logging
from gevent import monkey
import settings
from scheduler import Task
from runtime import Runtime
monkey.patch_all()

class TaskFactory(object):
    '''for every project, only one task instance is allowed running'''
    def __init__(self, project_name, do_action):
        pass

    def __new__(cls, project_name, do_action):
        task = Runtime().running_task.get(project_name)
        if task:
            if task.is_dead(): #重置僵尸任务
                del task
                task = None
            elif do_action == 'restart':
                task.stop()
                del task
                task = None
            else:
                return task
        task = Task(project_name)
        Runtime().running_task[project_name] = task
        return task

class Subscriber(object):
    '''subcribe message from publisher channel, change status of task'''
    def __init__(self):
        redis_client = redis.StrictRedis(**settings.redis_control_conf)
        self.channel = redis_client.pubsub()
        self.channel.subscribe(settings.redis_control_channel)

    def run(self):
        for msg in self.channel.listen():
            logging.debug(msg)
            print(msg)
            request_json = msg['data']
            try:
                request_body = json.loads(request_json)
            except Exception as e:
                print(e)
                continue
            is_assigned, project_name, do_action, run_params = self._extract(request_body)
            if not is_assigned: 
                continue
            logging.info('%s, %s, %s' %(project_name, do_action, datetime.datetime.now()))
            task = TaskFactory(project_name, do_action)
            if do_action == 'start' or do_action == 'restart':
                if task.is_idle():
                    gevent.spawn(task.start, **run_params)
            elif do_action == 'stop':
                gevent.spawn(task.stop)
            elif do_action == 'status':
                gevent.spawn(task.status)
            #gevent 进行非租塞调度
            gevent.getswitchinterval()

    def _extract(self, data):
        ips = data.get('ips')
        is_assigned = 1
        if ips and Runtime().local_ip not in ips: #检查本机IP在不在任务IP中
            is_assigned = 0
        project_name = data['project']
        if not project_name:
            raise Exception
        do_action = data['action']
        run_params = {
                    'package_name': project_name, 
                    'worknum': data.get('worknum', 0),
                    'sleep_interval': data.get('sleep_interval', 0), 
                    'queue_num': data.get('queue_num', 1),
                    'pull_size': data.get('pull_size', 100)}
        return is_assigned, project_name, do_action, run_params
