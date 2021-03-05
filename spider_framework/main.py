import sys
import multiprocessing
import json
import redis
import pymongo
from requestProcess import getResponse, spiderEngine
from responseProcess import responseProcessRegister as responseProcessor
from urlProcess import redisRun
from database.initilize import launch_database_server

def main():

    # launch_database_server()

    settings = json.load(open("/home/xkx/tech-doc/spider/visual_language_dataset_spider/spider_framework/config/ExampleSettings.json"))

    redisCli = redis.Redis(
        host=settings['redisHost'],
        port=settings['redisPort'],
        db=settings['redisDB'],
        decode_responses=True
    )
    mongoCli = pymongo.MongoClient(
        host=settings['mongoHost'],
        port=settings['mongoPort'],
        # 实例化mongoCLi的时候，不进行链接
        connect=False,
    )

    # 启动redis任务制造引擎
    # 存放原始url任务的集合名字
    # spiderSettings是一个从爬虫文件中导入的字典
    dbName = settings["dbName"]
    cltName = settings["cltName"]
    taskName = settings["taskName"]

    # 这个是爬虫引擎的个数，发动机的数量
    multiProNums = settings["multiProNums"]
    # 并发的数量
    concurrentCount = settings["concurrentCount"]
    # maxsize决定了que队列的容量，达到这个容量后，向里面添加元素会发送阻塞，
    queRequest = multiprocessing.Queue(maxsize=multiProNums*2)
    # taskName, concurrentCount, queRequest
    # redisRunning(redisCli, taskName, concurrentCount, queRequest, mulProNums)
    pRedisRun = multiprocessing.Process(target=redisRun,
                                        args=(redisCli, taskName, concurrentCount,
                                              queRequest, multiProNums))
    pRedisRun.start()

    # 启动爬虫引擎
    # queRequest, queReposne
    queReposne = multiprocessing.Queue()
    pList = [multiprocessing.Process(
        target=spiderEngine, args=(queRequest, getResponse, queReposne), name=f'{i}') for i in range(multiProNums)]
    [p.start() for p in pList]
    # 启动响应解析引擎。
    # mongoCli, taskName, dbName, cltName, parseResponse, queReposne
    multiprocessing.Process(target=responseProcessor.run,
                            args=(redisCli, mongoCli, taskName, dbName, cltName, queReposne)).start()
    # 阻塞等待url任务原始集合里面的url任务消耗完毕
    pRedisRun.join()
    [p.join() for p in pList]
    queReposne.put(None)


if __name__ == "__main__":
    main()