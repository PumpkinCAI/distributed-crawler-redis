# distributed-crawler-redis

## 背景

**注**: 项目原型是2015年写的，模块简单，易于改造，复杂工程推荐使用scrapy-redis.

- 爬虫任务，有大量的种子url,  要进行并发请求、分析获得数据。
- 爬虫为了反IP屏蔽，需要多节点工作。
- 多项目爬虫任务，调度基本相同，只有抓取和解析部分需要重写。
- 爬虫脚本经常更新，节点的脚本要自动拉取更新。

## 架构

![arch.jpg](https://raw.githubusercontent.com/PumpkinCAI/distributed-crawler-redis/main/arch.jpg)

1. **任务端**：上传最新脚本，数据写入redis队列，发布通知到各节点
2. **服务节点**：收到通知，启动任务调度器。从脚本服务器拉取最新脚本，从redis队列获取数据，调用脚本主类对数据进行处理，写入数据库。


## 特性

- [x] 节点上只需要部署一次，每次任务启动时节点自动拉取任务脚本

- [x] 可以同时运行不同的任务脚本，共用调度器，数据互不干扰

- [x] 任务端去中心化，可以在任何机器上运行，无需后台进程。

- [x] 任务端可以启动、停止各节点任务，可以查看各节点任务运行状态。

## 环境要求

- python 2.7, python 3+

- gevent

- redis

- requests

## 安装

首先需要部署一个ftp服务, 一个redis服务。

- 节点服务器 (建议使用ansible、docker等工具批量部署，使用supervisor守护进程。)

```sh
$ git clone https://github.com/PumpkinCai/distributed-crawler-redis.git
$ cd distributed-crawler-redis/
$ vi settings.py （settings of ftp service and redis service）
$ cd server
$ python server.py
```

- 任务端

```sh
$ git clone https://github.com/PumpkinCai/distributed-crawler-redis.git
$ cd distributed-crawler-redis/
$ cp -r sample xxx(your project name)
$ cd xxx
$ vi start_script.py(your crawler code)
$ python start_script.py
```

## 使用

- 启动任务: ```$ python start-script.py```
  
  ```python
  Publisher().start(project_name, worknum=3, sleep_interval=0, queue_num=1, pull_size=100)
  ```
  
  > worknum: 任务的并发数。用gevent的协程池进行调度，每个请求都是非阻塞的。仅当并发数为1时，为阻塞模式。  
  > 
  > sleep_interval: 这个参数只有在worknum=1的时候有效，任务请求被阻塞，每次请求之后等待。适用于反爬虫非常严厉的的情景。  
  > 
  > queue_num: 数据队列的数目，默认为一个队列。redis的列表类型做先进先出队列，在数据规模很大的时候，性能会显著下降，通过多队列的方式可以提高性能。  
  > 
  > pull_size: 一次请求拉取的数据数目，默认为100。每个节点一次网络请求拉取多项数据，可以提高性能。注意如果一次拉取太多会导致其他节点没有数据可以处理。  
  >
  > ips: 指定的工作节点IP列表， 默认为None, 所有节点都运行任务。


- 停止任务：```$ python stop-script.py```
- 查看各节点任务运行状态：```$ python status_script.py```

## 作者

[@PumpkinCAI](https://github.com/PumpkinCAI).

## 许可证

[MIT](LICENSE) © JunYI Cai
