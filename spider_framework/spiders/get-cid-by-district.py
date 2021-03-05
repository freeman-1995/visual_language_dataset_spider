import aiohttp
import json
import  redis
import  time
spiderSettings = {
    # redis配置
    'taskName': "get-cid",
    'redisHost': "127.0.0.1",
    'redisPort': 6379,
    'redisDB': 2,
    # MongoDB配置
    'mongoHost': "127.0.0.1",
    'mongoPort': 27017,
    "dbName": "51zxw-company",
    'cltName': "all-cid",
    # 这个是爬虫引擎的个数，发动机的数量,
    'multiProNums': 1,
    # 并发的数量
    'concurrentCount': 64,
}

redisCli = redis.Redis(host=spiderSettings['redisHost'],
                       port=spiderSettings['redisPort'],
                       db=spiderSettings['redisDB'],
                       decode_responses=True)
async def getResponse(urlTask, queReposne):
    method = "POST"
    # 加入urlTask是一个url
    # urlTask如果是一个id，我们需要构造出url
    # 比如说url=f"https://www.xxx.com/distrtct?cid={urlTask}"
    # # d:代表地区， 0 代表skip
    # urlTask=f"{d}__0"
    url = "http://221.15.248.244:5100/district/"
    d = urlTask.split("__")[0]
    skip = urlTask.split("__")[1]
    data = {"d": d, "findlimit": 50, "skip": skip}
    # print(time.asctime(),"-->>",urlTask,"$$$$$$$$$")
    try:
        async with aiohttp.ClientSession() as ss:
            response = await ss.post( url, data=data)
            if response.status == 200:
                text = await response.text()
                # 需要有错误处理机制，可以首先根据响应码来判断是否为200
                queReposne.put((urlTask, text))
    except Exception as e:
        print(urlTask,e)
        pass


def parseResponse(urlTask, text):
    # 解析网络响应结果 可以使用xpath或者是正则表达式来提取item
    # print(time.asctime(),"-->>",urlTask,"$$$$$$$$$")
    districtList=json.loads(text)
    d = urlTask.split("__")[0]
    skip = urlTask.split("__")[1]
    skipNext=int(skip)+50
    if len(districtList)==50:
        #如果页面返回的结果数量等于50个，才有下一页
        taskNew=f"{d}__{skipNext}"
        redisCli.sadd(spiderSettings["taskName"],taskNew)
    if len(districtList)==0:
        return dict()
    # cidList=list()
    for i in districtList:
        cid=i['_id']
        # cidList.append(cid)
        item=dict(_id=int(cid))
        yield item
    # item = dict(_id=urlTask,cidList=cidList)
    # # 当一个响应结果包含多条数据的时候我们可以将多条数据添加到一个列表当中作为
    # #一个字典返回，
    # # 也可以使用yield 返回多条数据
    #
    #
    # return item



