"""实现多引擎模式异步并发爬虫系统
三大引擎：
    任务引擎, 爬虫引擎, 解析引擎
"""
import sys
import redis
import asyncio
import pymongo
import multiprocessing
import importlib

# decode_responses参数设置为True，直接将获取的值转换utf-8模式的字符串


def redisRunning(redisCli, taskName, concurrentCount, queRequest, mulProNums):
    """redis任务制造引擎模块

    """
    # 存放url任务的集合key名称
    taskNameBuffer = taskName + "_buffer"
    taskNameFp = taskName + "_fp"
    while redisCli.scard(taskName) > 0:
        # 首先判断一下缓存集合是否存在 exsits
        # 如果buffer存在，则返回1 不存在返回0
        if not redisCli.exists(taskNameBuffer):
            # 将原始url任务集合当中的任务copy一份到url任务缓存中
            redisCli.sunionstore(taskNameBuffer, taskName)

        # 开始从缓存任务集合中提取url任务，
        # count代表返回url任务的数量，也就是我们并发的数量
        while True:
            urlTaskList = redisCli.spop(taskNameBuffer, count=concurrentCount)
            # urlTaskList=0代表缓存集合中的任务没有了，需要重新从原始任务集合当中复制
            if len(urlTaskList) == 0:
                break
            # 先判断一下 任务在不在指纹集合当中
            # 真正要放入队列的任务集合，请求成功过的url任务不再放入队列
            urlTaskListX = list()
            for urlTask in urlTaskList:
                # 返回true代表指纹存在，即之前请求成功过
                if not redisCli.sismember(taskNameFp, urlTask):
                    urlTaskListX.append(urlTask)
                else:
                    #如果指纹存在，则删除原始任务集合当中的任务
                    redisCli.srem(taskName,urlTask)
            # urlTaskListX=0代表 从缓存集合当中拿到的任务全部请求成功过
            if len(urlTaskListX) > 0:
                queRequest.put(urlTaskListX)
    # 任务结束的标志
    for i in range(mulProNums):
        queRequest.put(None)



async def spiderMain(*spiderS):
    await asyncio.gather(*spiderS)


def spiderEngine(queRequest, getResponse, queReposne):
    """网络爬虫引擎

    """
    while True:
        # 从任务队列当中提取要爬取的url任务
        urlTaskList = queRequest.get()
        if urlTaskList is not None:
            # asyncio,aiohttp
            # 先构造一个并发的请求函数，为协程
            # 先定义一个并发运行协程函数的最高层级入口点
            # spiderS=[getResponse() for i in range(100)]
            spiderS = [getResponse(urlTask, queReposne) for urlTask in urlTaskList]
            asyncio.run(spiderMain(*spiderS))
            ...
        else:
            break


def mongoInsert(mongoCli, dbName, cltName, item):
    collection = mongoCli[dbName][cltName]
    try:
        # item为空字典时候不添加到mongodb，但是也是请求成功的 可以删除这个url任务
        if item:
            # print("insert {} into mongodb".format(item))
            collection.insert_one(item)
    except:
        pass


# def responseEngine(mongoCli, taskName, dbName, cltName, parseResponse, queReposne):
#     # 从queResponse响应队列中获取响应结果
#     taskNameFp = taskName + "_fp"
#     while True:
#         queGet = queReposne.get()
#         # 结束响应处理的标志None
#         if queGet is None:
#             break
#         urlTask, text = queGet

#         # 解析网页响应结果text，
#         # item = parseResponse(urlTask, text)
#         for item in parseResponse(urlTask, text):
#         # 如果parseResponse是一个生成器的话，需呀遍历获取item
#         # mongoCli, dbName, cltName, item
#             mongoInsert(mongoCli, dbName, cltName, item)
#         # mongoInsert(mongoCli=mongoCli,dbName=dbName,item=item,cltName=cltName)
#         redisCli.smove(taskName, taskNameFp, urlTask)
#         redisCli.sadd(taskName, )


def responseEngine(mongoCli, taskName, dbName, cltName, parseResponse, queReposne):
    # 从queResponse响应队列中获取响应结果
    taskNameFp = taskName + "_fp"
    while True:
        queGet = queReposne.get()
        # 结束响应处理的标志None
        if queGet is None:
            break
        urlTask, text = queGet

        # 解析网页响应结果text，
        items, newUrlTasks = parseResponse.parse(urlTask, text)
        for item in items:
        # 如果parseResponse是一个生成器的话，需呀遍历获取item
        # mongoCli, dbName, cltName, item
            mongoInsert(mongoCli, dbName, cltName, item)
        # mongoInsert(mongoCli=mongoCli,dbName=dbName,item=item,cltName=cltName)
        redisCli.smove(taskName, taskNameFp, urlTask)
        for new_task in newUrlTasks:
            redisCli.sadd(taskName, new_task)


def multiMain(mongoCli, redisCLi, spiderSettings, getResponse, parseResponse, responseEngine):
    # 启动redis任务制造引擎
    # 存放原始url任务的集合名字
    # spiderSettings是一个从爬虫文件中导入的字典
    dbName = spiderSettings["dbName"]
    cltName = spiderSettings["cltName"]
    taskName = spiderSettings["taskName"]

    # 这个是爬虫引擎的个数，发动机的数量
    multiProNums = spiderSettings["multiProNums"]
    # 并发的数量
    concurrentCount = spiderSettings["concurrentCount"]
    # maxsize决定了que队列的容量，达到这个容量后，向里面添加元素会发送阻塞，
    queRequest = multiprocessing.Queue(maxsize=multiProNums*2)
    # taskName, concurrentCount, queRequest
    # redisRunning(redisCli, taskName, concurrentCount, queRequest, mulProNums)
    pRedisRun = multiprocessing.Process(target=redisRunning,
                                        args=(redisCLi, taskName, concurrentCount,
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
    multiprocessing.Process(target=responseEngine,
                            args=(mongoCli, taskName, dbName, cltName, parseResponse, queReposne)).start()
    # 阻塞等待url任务原始集合里面的url任务消耗完毕
    pRedisRun.join()
    [p.join() for p in pList]
    queReposne.put(None)


def getMyspider():
    # 动态的获取爬虫文件下的变量
    assert len(sys.argv) >= 2, "请输入正确的运行格式，python main <spider>"
    spiderName = sys.argv[1].split("/")[1].replace(".py", '')
    spider = importlib.import_module(f"spiders.{spiderName}")
    spiderSettings = spider.spiderSettings
    # 获取包下面的变量
    getResponse = spider.getResponse
    # getResponse=getattr(spider,"getResponse")
    # parseResponse = spider.parseResponse
    parseResponse = spider.VisualHuntResponseProcessor
    return spiderSettings, getResponse, parseResponse
    ...


if __name__ == "__main__":
    # 程序的运行方式为 python main.py 《爬虫文件》
    # print(sys.argv)
    # 获取一下爬虫文件名
    # 添加爬虫功能的思路，比如代理ip，哪里需要就往哪里添加，一层层的向上补充完善函数参数

    spiderSettings, getResponse, parseResponse = getMyspider()
    redisCli = redis.Redis(host=spiderSettings['redisHost'],
                           port=spiderSettings['redisPort'],
                           db=spiderSettings['redisDB'],
                           decode_responses=True)
    mongoCli = pymongo.MongoClient(
        host=spiderSettings['mongoHost'],
        port=spiderSettings['mongoPort'],
        # 实例化mongoCLi的时候，不进行链接
        connect=True,
    )
    multiMain(mongoCli, redisCli, spiderSettings, getResponse, parseResponse, responseEngine)
