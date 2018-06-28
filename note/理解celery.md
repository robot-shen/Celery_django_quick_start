# 介绍
【前言】 为什么要有celery
在程序的运行过程中，我们经常会碰到一些耗时耗资源的操作，为了避免它们阻塞主程序的运行，我们经常会采用多线程或异步任务。
比如，在 Web 开发中，对新用户的注册，我们通常会给他发一封激活邮件，而发邮件是个 IO 阻塞式任务，
如果直接把它放到应用当中，就需要等邮件发出去之后才能进行下一步操作，此时用户只能等待再等待。
更好的方式是在业务逻辑中触发一个发邮件的异步任务，而主程序可以继续往下运行。

Celery 是一个强大的分布式任务队列，它可以让任务的执行完全脱离主程序，甚至可以被分配到其他主机上运行。
我们通常使用它来实现异步任务（async task）和定时任务（crontab）。


1. Celery是什么?
Celery 是一个由 Python 编写的用来处理大量信息的分布式系统,它同时提供操作和维护分布式系统所需的工具。

Celery 专注于实时任务处理，支持任务调度。

说白了，它是一个**分布式队列的管理工具**，我们可以用 Celery 提供的接口快速实现并管理一个分布式的任务队列。

我们要理解 Celery 本身不是任务队列，它是**管理**分布式任务队列的**工具**，
它封装好了操作常见任务队列的各种操作，我们用它可以快速进行任务队列的使用与管理，
当然你也可以自己看 rabbitmq 等队列的文档然后自己实现相关操作都是没有问题的。

2. 什么是任务队列?

任务队列是一种在多线程或多机器间分发任务的机制。
(MQ是消息队列，AMQP是高级消息队列协议，是应用层协议的一个开放标准)

任务队列的输入是一个叫做task的单元，专门的worker进程会持续监听task queues，持续监视队列中是否有需要处理的新任务
worker还被翻译为职程，职业负责监听的一个进程。
A task queue’s input is a unit of work called a task. Dedicated worker processes constantly monitor task queues for new work to perform.

Celery通过消息进行通信，这个消息队列其实就是任务队列概念的主要部分，称为Broker。
中间人（Broker）在clients 和worker之间进行协调，常用的Broker是RabbitMQ, Redis。 
client向队列添加消息发起task，然后Broker把消息传给worker。**消息收、发是由broker完成的**
To initiate a task the client adds a message to the queue, the broker then delivers that message to a worker.

Celery 系统可包含多个worker和broker，具备高可用性和横向扩展能力

Celery 是用 Python 编写的，但协议可以用任何语言实现(语言无关)。
只是如果你恰好使用 Python 进行开发那么使用 Celery 就自然而然了。
迄今，已有 Ruby 实现的 RCelery 、node.js 实现的 node-celery 以及一个 PHP 客户端 ，也可以通过 using webhooks 实现语言互通。

3. 其他概念

 - 结果存储 Result Stores / backend

结果储存的地方：队列中的任务运行后的结果或状态需要被任务发送者知道，那么就需要一个地方储存这些结果，就是 Result Stores 了
> 常见的 backend 有 redis、Memcached 甚至常用的数据都可以  
`AMQP, Redis，memcached, MongoDB，SQLAlchemy, Django ORM，Apache Cassandra`

 - Workers(职程)
 
就是 Celery 中的工作者，类似与生产/消费模型中的消费者，其从队列中取出任务并执行
celery -A tasks worker --loglevel=info 启动一个worker进程
此时，worker进程开始监听tasks这个任务集合（待命状态）

```
app = Celery('tasks',  backend='redis://localhost:6379/0', broker='redis://localhost:6379/0') #配置好celery的backend和broker

@app.task  #普通函数装饰为 celery task
def add(x, y):
    return x + y
```

client 执行add函数，相当于向tasks任务集添加task
然后tasks被app这个Celery()实例中的broker传给worker进程 来执行
worker进程执行完，把结果给app中的backend。（直接给还是通过broker ？存疑）
大概就是这么个流程


【小结】
rabbitMQ or Redis做消息收发，celery来做队列的管理
celery可以给rabbitMQ 分发任务
worker 监听并执行任务
Result Stores / backend 接受存储任务结果



# 分块理解

## Celery的架构

Celery的架构由三部分组成，消息中间件（message broker），任务执行单元（worker）和任务执行结果存储（task result store）组成。

### 消息中间件

Celery本身不提供消息服务，但是可以方便的和第三方提供的消息中间件集成，包括，RabbitMQ,Redis,MongoDB等，这里我先去了解RabbitMQ,Redis。

### 任务执行单元

Worker是Celery提供的任务执行的单元，worker并发的运行在分布式的系统节点中

### 任务结果存储(Result Stores / backend)

Task result store用来存储Worker执行的任务的结果

celery支持的BACKEND可是太丰富了：
 - 数据库 使用SQLAlchemy支持的关系数据库
 - 缓存 使用memcached来存储结果
 - MongoDB 使用MongoDB来存储结果
 - Redis 使用Redis来存储结果
 - AMQP 将结果作为AMQP消息发送给AMQP
 - 还有cassandra ironcache couchbase

## celery换种角度看架构

 - celery beat 任务调度器，
Beat进程会读取配置文件的内容，周期性地将配置中到期需要执行的任务发送给任务队列。
有的任务需要它，非周期性执行的任务就不需要它了

 - celery worker
 执行任务的消费者，通常会在多台服务器运行多个消费者来提高执行效率
 
  - producer 生产者
调用了Celery提供的API、函数或者装饰器而产生任务并交给任务队列处理的都是任务生产者。

 - Backend
任务处理完后保存状态信息和结果，以供查询











