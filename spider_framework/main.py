import sys
import multiprocessing
import json
import redis
import pymongo
from requestProcess import getResponse, spiderEngine, saveImage, saveResponse
from responseProcess import responseProcessRegister as responseProcessor
from urlProcess import redisRun
from database.initilize import launch_database_server

def main():
    # launch_database_server()

    settings = json.load(open("/home/xkx/tech-doc/spider/visual_language_dataset_spider/spider_framework/config/ExampleSettings.json"))

    print(settings)

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

    # init url task
    # redisCli.delete("visualhunt")
    # redisCli.delete("visualhunt_buffer")
    # redisCli.delete("visualhunt_fp")

    redisCli.delete("unsplash")
    redisCli.delete("unsplash_buffer")
    redisCli.delete("unsplash_fp")

    redisCli.delete("unsplash_save")
    redisCli.delete("unsplash_save_buffer")
    redisCli.delete("unsplash_save_fp")

    redisCli.delete("task_map")
    redisCli.delete("img_text_map")
    redisCli.delete("img_map")

    redisCli.sadd("unsplash", "https://unsplash.com/napi/topics/color-theory/photos?page=1&per_page=10")
    redisCli.hset("task_map", key="https://unsplash.com/napi/topics/color-theory/photos?page=1&per_page=10", value=0)

    redisCli.sadd("unsplash", "https://visualhunt.com/photos/cat/1")
    redisCli.hset("task_map", key="https://visualhunt.com/photos/cat/1", value=1)

    # redisCli.sadd("unsplash", "https://unsplash.com/")
    # redisCli.hset("task_map", key="https://unsplash.com/", value=2)


    # 启动redis任务制造引擎
    # 存放原始url任务的集合名字
    # spiderSettings是一个从爬虫文件中导入的字典
    dbName = settings["dbName"]
    cltName = settings["cltName"]
    taskName = settings["taskName"]
    saveName = settings["saveName"]

    # 这个是爬虫引擎的个数，发动机的数量
    multiProNums = settings["multiProNums"]
    # 并发的数量
    concurrentCount = settings["concurrentCount"]
    # maxsize决定了que队列的容量，达到这个容量后，向里面添加元素会发送阻塞，
    queRequest = multiprocessing.Queue(maxsize=multiProNums*2)
    saveQueRequest = multiprocessing.Queue(maxsize=multiProNums*2)
    # taskName, concurrentCount, queRequest
    # redisRunning(redisCli, taskName, concurrentCount, queRequest, mulProNums)
    pRedisRun = multiprocessing.Process(target=redisRun,
                                        args=(redisCli, taskName, concurrentCount,
                                              queRequest, multiProNums))
    pRedisRun.start()

    pRedisSave = multiprocessing.Process(target=redisRun,
                                        args=(redisCli, saveName, concurrentCount,
                                              saveQueRequest, multiProNums))
    pRedisSave.start()

    # 启动爬虫引擎
    # queRequest, queReposne
    queReposne = multiprocessing.Queue()
    pList = [multiprocessing.Process(
        target=spiderEngine, args=(queRequest, getResponse, queReposne), name=f'{i}') for i in range(multiProNums)]
    [p.start() for p in pList]

    # 图片保存
    pList = [multiprocessing.Process(
        target=saveImage, args=(redisCli, saveName, saveQueRequest, saveResponse), name=f'{i}') for i in range(multiProNums)]
    [p.start() for p in pList]

    # 启动响应解析引擎。
    # mongoCli, taskName, dbName, cltName, parseResponse, queReposne
    multiprocessing.Process(target=responseProcessor.run,
                            args=(redisCli, mongoCli, taskName, saveName, dbName, cltName, queReposne)).start()
    # 阻塞等待url任务原始集合里面的url任务消耗完毕
    pRedisRun.join()
    [p.join() for p in pList]
    queReposne.put(None)


if __name__ == "__main__":
    main()
