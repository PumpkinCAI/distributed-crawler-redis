# -*- coding: utf8 -*-
import socket
class Runtime(object):
    '''global data'''
    _instance = None
    running_task = {}
    local_ip = str(socket.gethostbyname_ex(socket.gethostname())[2][0]) #get ip of the machine

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

