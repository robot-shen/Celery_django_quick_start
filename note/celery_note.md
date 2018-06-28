
# 一、介绍
详见【理解celery.md】 文件

# 二、上手使用

## 选择中间件
Celery的默认broker是RabbitMQ（这是句废话，默认的使用也需要配置）
    使用时：app = Celery('tasks', broker='pyamqp://guest@localhost//')
如果想用redis做broker：
    app = Celery('tasks', broker='redis://140.143.228.252:6379/0')
    
使用格式为：
    redis://:password@hostname:port/db_number

## 其他
celery创建worker 用以执行任务
add.delay(命令) 发消息
redis作为消息中间件，
redis作为backend，存储消息 存储执行结果

# 三、小试牛刀

## 实验环境：
```
远端： redis-server  140.143.228.252  CentOS Linux release 7.5.1804 (Core) 
密码置空： config set requirepass ''
保护模式关闭：config set protected-mode no

本地：win7 64 
    redis ：python - redis
    celery: python - celery
```

## 官网quickstart
```
yum install redis-server
pip install redis
pip install celery
```
远端redis：改配置文件 或者 使用redis-cli 设置sever端

 - Tasks

tasks.py
```
from celery import Celery

app = Celery('tasks',  backend='redis://140.143.228.252:6379/0', broker='redis://140.143.228.252:6379/0') #配置好celery的backend和broker
# 带密码：redis://yourpwd@140.143.228.252:6379/0

@app.task  #普通函数装饰为 celery task
def add(x, y):
    return x + y
```

 - worker
 
然后在目录下，cmd运行  `celery -A tasks worker --loglevel=info`
windows下可能需要安装eventlet模块(pip install eventlet)
celery worker -A tasks --loglevel=info -P eventlet

运行 tasks 这个任务集合的 worker 进行工作

运行成功提示信息：
此时broker中还没有任务，worker此时相当于待命状态
```
 -------------- celery@ZhanDouJi v4.2.0 (windowlicker)
---- **** -----
--- * ***  * -- Windows-7-6.1.7601-SP1 2018-06-26 11:49:18
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         tasks:0x377f978
- ** ---------- .> transport:   redis://140.143.228.252:6379/0
- ** ---------- .> results:     redis://140.143.228.252:6379/0
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . tasks.add
  
[2018-06-26 11:49:19,544: INFO/MainProcess] mingle: all alone
[2018-06-26 11:49:19,622: INFO/MainProcess] celery@ZhanDouJi ready.
```



 - 然后新开一个cmd，或者直接在pycharm的terminal里边启动一个python

```
>>> from tasks import add
>>> add.delay(8,8) # 使用 apply_async() 来调度任务也可以
<AsyncResult: 1cf03eb7-995c-4dd6-9b3b-a593a2b3db29>
>>> result.ready()
False
>>> result.get()  --- 报错

在celery窗口启动celery，然后：
>>> result = add.delay(4, 4)
>>> result.ready()
True
>>> result.get()

celery窗口会打印两个结果 16 8
```

# 三、再进一步

## 回顾上面例子
 - celery的启动
上例中，启动celery进程是在cmd中
    `celery -A tasks worker --loglevel=info`

tasks 就是同目录下，存放task的py文件
其中的普通函数 add() 被 @app.task 装饰为 celery task

 - client运行
通过新的cmd窗口，执行add.delay(8,8) 来向worker发任务


## 通过py文件运行(省点事)
参考链接：[celery上手](https://www.cnblogs.com/ctztake/p/8964939.html)
start_celery项目中，我们新建了trigger.py文件

内容如下：
```
import time
from tasks import add
result = add.delay(4, 4) #不要直接 add(4, 4)，这里需要用 celery 提供的接口 delay 进行调用
while not result.ready():
    time.sleep(1)
print ('task done: {0}'.format(result.get()))
```
通过第三方的py程序调用task函数，省点事

## 配置
配置可以直接在应用上设置，也可以使用一个独立的配置模块。
所有的配置选项参见官网：[Configuration and defaults](http://docs.jinkan.org/docs/celery/configuration.html#configuration)

### 程序内配置
 - 单条配置
`app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.timezone = 'UTC'`

 - 多条配置
```
app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='Europe/Oslo',
    CELERY_ENABLE_UTC=True,
)
```

### 独立文件配置
实际上，大家都是用配置文件做设置的。没哪个傻蛋在代码里写配置

在你的包里边新建一个py文件，按需起名，比如 celery_config.py
后边要做的那个周期/定时任务，配置全写在这个里边

【配置示例】
```
## Broker settings.
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('myapp.tasks', )

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'db+sqlite:///results.db'

CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
```

【应用】
调用 config_from_object() 来让 Celery 实例加载配置模块：
在app装饰函数之前，先给app加载配置(记得导入)：
> app.config_from_object('celery_config')

在配置文件中配置好BROKER_URL 和 CELERY_RESULT_BACKEND
这样我们在实例化app时就不需要再写broker和backend了，更为灵活简洁

```
app = Celery('tasks') 只需要给起个名字就好
app.config_from_object('celery_config')
def add(x, y):
    time.sleep(5)     # 模拟耗时操作
    return x + y
```

# 搞个小工程

参考[celery抽筋扒皮](https://blog.csdn.net/yangxiaodong88/article/details/79233027)

 - 项目结构
```
celery_demo                    # 项目根目录
    ├── celery_app             # 存放 celery 相关文件
    │   ├── __init__.py
    │   ├── celeryconfig.py    # 配置文件
    │   ├── task1.py           # 任务文件 1
    │   └── task2.py           # 任务文件 2
    └── client.py              # 应用程序
```

 - init.py
```
from celery import Celery

app = Celery('demo')                                # 创建 Celery 实例
app.config_from_object('celery_app.celeryconfig')   # 通过 Celery 实例加载配置模块
```

 - celeryconfig.py 
```
BROKER_URL = 'redis://140.143.228.252:6379/0'               # 指定 Broker
CELERY_RESULT_BACKEND = 'redis://140.143.228.252:6379/0'  # 指定 Backend

CELERY_TIMEZONE='Asia/Shanghai'                     # 指定时区，默认是 UTC
# CELERY_TIMEZONE='UTC'

# CELERY_INCLUDE 也可以导入
CELERY_IMPORTS = (                                  # 指定导入的任务模块
    'celery_app.task1',
    'celery_app.task2'
)
```

 - task1
```
import time
from celery_app import app

@app.task
def add(x, y):
    time.sleep(2)
    return x + y

```

 - task2
```
import time
from celery_app import app

@app.task
def multiply(x, y):
    time.sleep(2)
    return x * y
```

 - client
```
from celery_app import task1
from celery_app import task2

task1.add.apply_async(args=[2, 8])        # 也可用 task1.add.delay(2, 8)
task2.multiply.apply_async(args=[3, 7])   # 也可用 task2.multiply.delay(3, 7)

print ('一个加法，一个乘法')
```

## 启动celery进程
windows-cmd

celery -A celery_app worker --loglevel=info -P eventlet

注意了：这里不再用tasks.py这种文件名作为参数了
celery -A tasks worker --loglevel=info -P eventlet
因为celery需要找的是Celery()实例
以前是tasks.py提供给它，现在是celery_app的init文件提供给它

这个实例包含了建立worker所需要的全部信息：
比如 worker名字 CELERY_IMPORTS broker backend等

**后台启动(守护进程)**
链接：[ the daemonization tutorial.](http://docs.celeryproject.org/en/latest/userguide/daemonizing.html#daemonizing)
开启：celery multi start w1 -A proj -l info
重启：celery  multi restart w1 -A proj -l info
stop：celery multi stop w1 -A proj -l info
干完活再stop：celery multi stopwait w1 -A proj -l info


## 运行client程序发任务啦

运行 $ python client.py，它会发送两个异步任务到 Broker，在 Worker 的窗口我们可以看到如下输出
```
[2018-06-27 21:31:14,030: INFO/MainProcess] Received task: celery_app.task1.add[
36a7d2df-08fc-45ee-a2dd-fdc1bbbc94b9]
[2018-06-27 21:31:14,043: INFO/MainProcess] Received task: celery_app.task2.mult
iply[f193e9c7-dea7-40c9-9c03-6d6db8d541d9]
[2018-06-27 21:31:16,067: INFO/MainProcess] Task celery_app.task2.multiply[f193e
9c7-dea7-40c9-9c03-6d6db8d541d9] succeeded in 2.0280000000002474s: 21
[2018-06-27 21:31:16,069: INFO/MainProcess] Task celery_app.task1.add[36a7d2df-0
8fc-45ee-a2dd-fdc1bbbc94b9] succeeded in 2.0280000000002474s: 10
```

## 题外话
通过上边工程我们发现：
client给worker发送task依靠的是 delay() 或 apply_async() 方法

delay()源码：
```
    def delay(self, *args, **kwargs):
        """Star argument version of :meth:`apply_async`.

        Does not support the extra options enabled by :meth:`apply_async`.

        Arguments:
            *args (Any): Positional arguments passed on to the task.
            **kwargs (Any): Keyword arguments passed on to the task.
        Returns:
            celery.result.AsyncResult: Future promise.
        """
        return self.apply_async(args, kwargs)
```
delay()调用了apply_async()。是个快捷方法，支持的参数有限
apply_async()才是client的灵魂所在呀

apply_async()源码
```
    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
                    link=None, link_error=None, shadow=None, **options):

        # 中间做了好多事
        
        return app.send_task(
            self.name, args, kwargs, task_id=task_id, producer=producer,
            link=link, link_error=link_error, result_cls=self.AsyncResult,
            shadow=shadow, task_type=self,
            **options
        )
```

apply_async()参数：
```
apply_async(args=(), kwargs={}, route_name=None, **options)

常用参数：

countdown：指定多少秒后执行任务
task1.apply_async(args=(2, 3), countdown=5) # 5 秒后执行任务

eta (~datetime.datetime)：指定任务被调度的具体时间，参数类型是 datetime
from datetime import datetime, timedelta
# 10秒后执行multiply任务
task1.multiply.apply_async(args=[3, 7], eta=datetime.utcnow() + timedelta(seconds=10))

expires：任务过期时间，参数类型可以是 float，也可以是 datetime
expires (float, ~datetime.datetime)
Datetime or seconds in the future for the task should expire.
The task won't be executed after the expiration time.

```
**指定eta参数，就是定时任务了**


其他参数：
```
shadow (str) connection (kombu.Connection) retry (bool)
retry_policy (Mapping) queue (str, kombu.Queue) exchange (str, kombu.Exchange)
 routing_key (str) priority (int) serializer (str) compression (str)
link link_error producer add_to_parent publisher headers
```

这里边有些参数与config文件里的参数重合，也就是说celery允许你调用的时候自己指定某些参数

## 周期任务
最开始就说了，celery的两大功能是异步任务和定时任务
async task 和 celery beat

在celeryconfig.py 文件增加如下代码
```
from datetime import datetime,timedelta
from celery.schedules import crontab

# schedules
CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
         'task': 'celery_app.task1.add',
         'schedule': timedelta(seconds=30),       # 每 30 秒执行一次
         'args': (5, 8)                           # 任务函数参数
    },
    'multiply-at-some-time': {
        'task': 'celery_app.task2.multiply',
        'schedule': crontab(hour=9, minute=50),   # 每天早上 9 点 50 分执行一次
        'args': (3, 7)                            # 任务函数参数
    }
}
```
 - 启用

启动 Celery Worker 进程，在项目的根目录下执行下面命令
celery -A celery_app worker --loglevel=info -P eventlet

新开的cmd窗口/pycharm的terminal中：开启任务调度器
celery beat -A celery_app
或者 celery -A celery_app beat --loglevel=info 可显示日志查看 Scheduler状态
beat进程启动会产生一些运行文件，默认保存在当前路径下
```
celery beat v4.1.1 (latentcall) is starting.
__    -    ... __   -        _
LocalTime -> 2018-06-27 22:24:36
Configuration ->
    . broker -> redis://140.143.228.252:6379/0
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule
    . logfile -> [stderr]@%WARNING
    . maxinterval -> 5.00 minutes (300s)

```


开worker的那个窗口：
```
···\celery_pj\celery_bapi>celery -A celery_app worker --loglevel=info -P eventlet

 -------------- celery@LS--20160928YTI v4.1.1 (latentcall)
---- **** -----
--- * ***  * -- Windows-7-6.1.7601-SP1 2018-06-27 22:24:06
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         demo:0x43d0358
- ** ---------- .> transport:   redis://140.143.228.252:6379/0
- ** ---------- .> results:     redis://140.143.228.252:6379/0
- *** --- * --- .> concurrency: 4 (eventlet)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery


[tasks]
  . celery_app.task1.add
  . celery_app.task2.multiply

[2018-06-27 22:24:06,560: INFO/MainProcess] Connected to redis://140.143.228.252
:6379/0
[2018-06-27 22:24:06,596: INFO/MainProcess] mingle: searching for neighbors
[2018-06-27 22:24:07,785: INFO/MainProcess] mingle: all alone
[2018-06-27 22:24:07,869: INFO/MainProcess] celery@LS--20160928YTI ready.
[2018-06-27 22:24:07,911: INFO/MainProcess] pidbox: Connected to redis://140.143
.228.252:6379/0.

[2018-06-27 22:25:06,208: INFO/MainProcess] Received task: celery_app.task1.add[
8688ee42-4f28-4109-8e1d-6beb05c1a9b3]
[2018-06-27 22:25:08,236: INFO/MainProcess] Task celery_app.task1.add[8688ee42-4
f28-4109-8e1d-6beb05c1a9b3] succeeded in 2.0279999999984284s: 13

[2018-06-27 22:25:36,099: INFO/MainProcess] Received task: celery_app.task1.add[
340c9883-3a45-4e1e-89d8-57a4e6b475c1]
[2018-06-27 22:25:38,110: INFO/MainProcess] Task celery_app.task1.add[340c9883-3
a45-4e1e-89d8-57a4e6b475c1] succeeded in 2.0119999999988067s: 13
```
可以看到worker中包含两个任务，
celery_app.task1.add 每隔30秒执行一次
celery_app.task2.multiply 每天早上执行一次(所以我们看不到日志)




# 再聊点其他的

## 碎碎念
 - celery有啥用
学习一种技术，一定是为了解决问题而不是炫技或zb。
① web场景，占用时间较长 的任务交给celery异步执行
② 定时任务，就是定时/周期性任务
只要是同时执行的任务都可以搞成异步啊

 - celery特性
1. 方便地查看定时任务的执行情况，比如执行是否成功、当前状态、执行任务花费的时间等。
2. 可以使用功能齐备的管理后台或者命令行添加、更新、删除任务。
3. 方便把任务和配置管理相关联。
4. 可选多进程、Eventlet和Gevent三种模式并发执行。
5. 提供错误处理机制。
提供多种任务原语，方便实现任务分组、拆分和调用链。  
支持多种消息代理和存储后端。  

 - **celery并发相关**
celery -A mytask worker -l info
启动后的窗口显示一些值
```
- ** ---------- [config]
- ** ---------- .> app:         tasks:0x377f978
- ** ---------- .> transport:   redis://140.143.228.252:6379/0
- ** ---------- .> results:     redis://140.143.228.252:6379/0
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
```
concurrency: 4 (prefork) 默认按照cpu核心数开启相应数的进程
*启动时加 -c 选项，自定义进程数*
除了prefork池，Celery还支持使用Eventlet，Gevent和线程

[Eventlet的使用](http://docs.jinkan.org/docs/celery/userguide/concurrency/eventlet.html)
prefork进程池，进程有局限，阻塞任务还是效率低。
eventlet底层是epoll实现，效率高。pip安装相关模块，启动时 -P 参数就ok了
celery worker -l info --concurrency=1000 --pool=eventlet
celery worker -P eventlet -c 1000


## 再来一个例程

[知乎-董伟明-celery](https://zhuanlan.zhihu.com/p/22304455)
这个例程里用了**celery.py**这种作死的命名方式

 - 程序结构
```
  proj
    ├── __init__.py         # 包
    ├── celery.py           # 主程序
    ├── celeryconfig.py     # 配置文件
    └── tasks.py            # 任务文件
```

 - 主程序celery.py
```
from __future__ import absolute_import
# 拒绝隐式引入，因为celery.py的名字和celery的包名冲突，需要使用这条语句让程序正确地运行

from celery import Celery

app = Celery('proj', include=['proj.tasks'])
app.config_from_object('proj.celeryconfig')

if __name__ == '__main__':
    app.start()
```

 - 任务文件 tasks.py
 ```
from __future__ import absolute_import
from proj.celery import app
@app.task
def add(x, y):
    return x + y
 ```
 
 - celeryconfig.py
 ```
BROKER_URL = 'amqp://dongwm:123456@localhost:5672/web_develop' # 使用RabbitMQ作为消息代理

CELERY_RESULT_BACKEND = 'redis://localhost:6379/0' # 把任务结果存在了Redis

CELERY_TASK_SERIALIZER = 'msgpack' # 任务序列化和反序列化使用msgpack方案

CELERY_RESULT_SERIALIZER = 'json' # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON

CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 # 任务过期时间，不建议直接写86400，应该让这样的magic数字表述更明显

CELERY_ACCEPT_CONTENT = ['json', 'msgpack'] # 指定接受的内容类型
 ```
------------------
celery -A proj worker -l info
-A参数默认会寻找proj.celery这个模块，其实使用celery作为模块文件名字不怎么合理
它在文件夹下自己寻找名为celery的模块！

【官网app参数解释】
celery worker --app=proj -l info
-A 是--app简写

假如-A 为文件夹(包)名，以proj为例：
celery -A proj worker -l info
1. celery会在proj下寻找 proj.app proj.celery 
2. 或者proj下其他任何一个能返回Celery实例的模块
3. 如果上边跑完还没找到celery实例
    proj.celery.app,
    proj.celery.celery
    或者proj.celery里边任何返回celery实例的函数

假如-A 为文件名
celery -A mytask worker -l info

综上，即使celery有自己找celery.py提取实例的机制，
也应该禁止celery有关的工程里出现任何以celery.py命名的文件
------------------
 - 指定队列
 
Celery非常容易设置和运行，通常它会使用默认的名为celery的队列用来存放任务。
我们可以修改相关的队列，使用优先级不同的队列来确保高优先级的任务不需要等待就得到响应

假设我们有 web.xx 和 task.xx 两个任务 
```
from kombu import Queue

CELERY_QUEUES = ( # 定义任务队列
Queue('default', routing_key='task.#'), # 路由键以“task.”开头的消息都进default队列
Queue('web_tasks', routing_key='web.#'), # 路由键以“web.”开头的消息都进web_tasks队列
)

CELERY_DEFAULT_EXCHANGE = 'tasks' # 默认的交换机名字为tasks

CELERY_DEFAULT_EXCHANGE_TYPE = 'topic' # 默认的交换类型是topic

CELERY_DEFAULT_ROUTING_KEY = 'task.default' # 默认的路由键是task.default，这个路由键符合上面的default队列

CELERY_ROUTES = {
    'projq.tasks.add': { # tasks.add的消息会进入web_tasks队列
    'queue': 'web_tasks',
    'routing_key': 'web.add',
    }}
```

 celery -A projq worker -Q web_tasks -l info

上述worker只会执行web\_tasks中的任务，我们可以合理安排消费者数量，让web_tasks中任务的优先级更高。




















