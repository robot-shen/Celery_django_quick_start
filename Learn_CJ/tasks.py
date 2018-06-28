#__author:  Administrator
#date:  2017/2/21

# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time,datetime

@shared_task
def add(x, y):
    print("running task add...")
    time.sleep(10)
    return x + y


@shared_task
def mul(x, y):
    return x * y

@shared_task
def now_time():
    t1 = time.time()
    t2 = datetime.datetime.now()
    t2 = t2.strftime( '%y-%m-%d %I:%M:%S %p' )
    return [t1,t2]


@shared_task
def xsum(numbers):
    return sum(numbers)