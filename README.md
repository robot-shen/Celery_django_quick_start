
# Celery_django快速启动

快速启动：按照官网例程，结合自己的使用经验，整理了一版快速project

[celery_note.md](https://github.com/robot-shen/Celery_django_quick_start/blob/master/note/celery_note.md) 中记录了一些更为详细的celery应用事项，同时也有官网demo的优化应用方式

相关教程：[博客 - clery (未更新)](http://www.cnblogs.com/jinshen/)

[文档：Using Celery with Django 3.1 旧版](http://docs.jinkan.org/docs/celery/django/first-steps-with-django.html)

[文档：Using Celery with Django 4.2 新版](http://docs.celeryproject.org/en/master/django/first-steps-with-django.html)

【注意】  
以前的版本Celery需要一个单独的库来与Django一起工作，但从3.1开始，情况就不再一样了。

现在直接支持Django，因此该文档仅包含集成Celery和Django的基本方法。您将使用与非Django用户相同的API，
因此建议您首先阅读Celery的First Steps教程，然后返回到本教程。当你有一个工作示例时，你可以继续下一步指南。

【注意】  
Celery 4.0支持Django 1.8和更新版本。对于Django 1.8之前的版本，请使用Celery 3.1。


1. 建立proj/proj/celery.py 文件
2. init.py里边引入celery.py
   celery.py 是官网例程起的名字，以后自己做的时候以app.py命名，不给自己留坑
   celery.py是celery的入口文件，里边有一些设置
   ```python
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Celery_django.settings')
    
    app = Celery('CeleryTest')
    
    app.config_from_object('django.conf:settings', namespace='CELERY')
    
    app.autodiscover_tasks()
    ```
3. *__init__.py*
包初始化文件，引导到celery.py里边的 app celery实例
```python
from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app
__all__ = ['celery_app']
```

4. settings.py
```
CELERY_BROKER_URL = 'redis://192.168.1.104:6379/0'
CELERY_RESULT_BACKEND = 'redis://192.168.1.104:6379/0'
```

5. 使用@shared_task装饰器

该@shared_task装饰可以让你无需任何具体的应用程序实例创建任务

Learn_CJ 下的 tasks.py 文件里边写了很多task函数
必须以tasks.py命名，autodiscover_tasks()才能发现这些任务
@shared_task 保证的是不同app可以共用celery实例

6. 终端启动命令

`\···\Celery_django>celery -A Celery_django worker -l info -P eventlet`

Celery_django 为工程所在文件夹




# 使用django的数据库
Using the Django ORM/Cache as a result backend
1. pip install django-celery-results
2. django-celery-results 设置 installed app

    **设置的名字是 django_celery_results**
    
3. 创建数据库表
python manage.py migrate django_celery_results
4. 配置Celery以使用django-celery结果后端
settings.py中
CELERY_RESULT_BACKEND = 'django-db'

对于缓存后端，您可以使用：
`CELERY_RESULT_BACKEND = 'django-cache'`


# django-celery-beat定期任务
[官网链接](http://docs.celeryproject.org/en/master/userguide/periodic-tasks.html#beat-custom-schedulers)
1. pip install django-celery-beat
2. INSTALLED_APPS = (
        ...,
        'django_celery_beat',
    )
3. python manage.py migrate
4. Start the celery beat service using the django_celery_beat.schedulers:DatabaseScheduler scheduler:
> celery -A proj beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
5. Django-Admin中设置定时任务

# 使用db存储定时任务
 - 数据库  
 多了 django_celery_beat_ 开头的5张表
 
 - 在admin管理页面:有这3张表
 
Crontabs： 年月周日时分 - 任务周期指定(仅周期)  
Intervals ：日时分秒微秒 - 任务周期指定(仅周期)  
Periodic tasks ：  
```
Periodic tasks:
celery.backend_cleanup: 0 4 * * * (m/h/d/dM/MY) 默认建立的字段
task 指定name，选择已在项目文件注册的task
     选择Schedule相关参数(Interval/crontab/solar)
     添加Arguments 
     添加 Execution Options
```
Solar events：根据日出，日落，黎明或黄昏执行  

【注意】  
> 需要注意的是，django只是把这些任务相关的数据存在自己数据库了而已  
django并没有发送task的功能  
还得是celery beat调度器来向队列发任务

**启动beat时加 -S 参数**  

`celery -A Celery_django beat -l info -S django`



# 启动worker进程

`celery -A proj worker -l info (-P eventlet)`

 - 多进程(默认)  
 
concurrency: 4 (prefork)   
celery默认按照cpu核心数开启相应数的进程，需要增加进程数 加`-c`参数

 - 多线程  
 
使用eventlet模块(pip install eventlet),-c 指定线程数  
`celery worker -P eventlet -c 1000`

 - 守护进程  
 
[守护进程的开启](http://docs.celeryproject.org/en/master/userguide/daemonizing.html#daemonizing)









