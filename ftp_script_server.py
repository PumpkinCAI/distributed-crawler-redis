# -*- coding: utf-8 -*-
import os
import sys
from ftplib import FTP
import logging
import settings
class FtpServer():
    '''ftp server for script'''
    def __init__(self, host=None, port=21, user=None, password=None):
        self.ftp = FTP()
        self.ftp.set_debuglevel(0)
        self.ftp.connect(host, port)
        self.ftp.login(user, password)
        logging.debug(self.ftp.getwelcome()) ##显示ftp服务器欢迎信息
        self.bufsize = 1024

    def download_file(self, filename, local_dir='./', remote_dir = './'):
        logging.info('downloading file')
        local_path = os.path.join(local_dir, os.path.basename(filename))
        remote_path = os.path.join(remote_dir, os.path.basename(filename))
        file_handler = open(local_path,'wb')
        self.ftp.retrbinary('RETR %s' % remote_path, file_handler.write, self.bufsize)#接收服务器上文件并写入本地文件
        file_handler.close()
        logging.info('file downloaded')
        return open(local_path, 'rb').read()

    def upload_file(self, filename, local_dir='./', remote_dir='./'):
        local_path = os.path.join(local_dir, os.path.basename(filename))
        remote_path = os.path.join(remote_dir, os.path.basename(filename))
        logging.info('uploading file')
        file_handler = open(local_path,'rb')
        self.ftp.storbinary('STOR %s' %remote_path, file_handler, self.bufsize)#上传文件
        file_handler.close()
        logging.info('file uploaded')

    def upload_dir(self, local_dir, remote_dir):
        try:
            self.ftp.cwd(remote_dir)
        except Exception:
            self.ftp.mkd(remote_dir)
            self.ftp.cwd(remote_dir)
        for filename in os.listdir(local_dir):
            if filename.endswith('.pyc'):
                continue
            if filename.startswith('__'):
                continue
            self.upload_file(filename, local_dir=local_dir)
            
    def download_dir(self, local_dir, remote_dir):
        self.ftp.cwd(remote_dir)
        try:
            os.chdir(local_dir)
        except Exception:
            os.mkdir(local_dir)
            os.chdir(local_dir)
        remote_files = self.ftp.nlst()
        for filename in remote_files:
            if filename.endswith('.pyc'):
                continue
            if filename.startswith('__'):
                continue
            self.download_file(filename)

    def close(self):
        self.ftp.quit()

def ftp_upload_dir(directory):
    ftp_server = FtpServer(**settings.script_ftp_conf)
    ftp_server.upload_dir('../'+ directory, './' + directory) 
    ftp_server.close()

def ftp_download_dir(directory=None):
    ftp_server = FtpServer(**settings.script_ftp_conf)
    resp = ftp_server.download_dir('../' + directory, './' + directory) 
    ftp_server.close()
    return resp

