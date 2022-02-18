import sys
sys.path.append('../')
from publisher import Publisher
import time
import redis
import sys
import settings
import os
if __name__ == '__main__':
    package_path = os.getcwd()
    project_name = os.path.basename(package_path) 
    Publisher().status(project_name)
    time.sleep(10)
    status_channel = '%s:status' %(project_name)
    status_db = redis.StrictRedis(**settings.redis_status_conf)
    cluster_status = status_db.hgetall(status_channel)
    for node, status in cluster_status.iteritems():
        print('%s:%s' %(node, status))

