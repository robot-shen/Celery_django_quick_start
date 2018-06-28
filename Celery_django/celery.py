#__author:  Administrator
#date:  2017/2/21

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Celery_django.settings')

app = Celery('CeleryTest')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# settings内关于celery的设置，以CELERY_ 格式书写
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# 自动加载所有django app中的tasks任务 ,必须以tasks.py命名
app.autodiscover_tasks()

# bind = True 选项来引用当前任务实例(self)
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


