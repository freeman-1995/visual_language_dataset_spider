import json
import aiohttp
from lxml import  etree
from bs4 import BeautifulSoup

spiderSettings = {
    # redis配置
    'taskName': "visualhunt_test",
    'redisHost': "127.0.0.1",
    'redisPort': 6379,
    'redisDB': 0,
    # MongoDB配置
    'mongoHost': "127.0.0.1",
    'mongoPort': 27017,
    "dbName": "visualhunt_test",
    'cltName': "visualhunt_test",
    # 这个是爬虫引擎的个数，发动机的数量,
    'multiProNums': 1,
    # 并发的数量
    'concurrentCount': 1,
}


async def getResponse(urlTask, queReposne):
    method = "GET"
    # 加入urlTask是一个url
    # urlTask如果是一个id，我们需要构造出url
    # 比如说url=f"https://www.xxx.com/distrtct?cid={urlTask}"
    url = urlTask
    try:
        async with aiohttp.ClientSession() as ss:
            response = await ss.request(method, url)
            if response.status == 200:
                text = await response.text()
                # 需要有错误处理机制，可以首先根据响应码来判断是否为200
                queReposne.put((urlTask, text))
    except:
        pass


def parseResponse(urlTask, text):
    # 解析网络响应结果 可以使用xpath或者是正则表达式来提取item
    item = dict(_id=urlTask)
    html=etree.HTML(text)
    dataList=html.xpath('//div[@id="s-top-left"]/a/text()')
    item["dataList"]=dataList
    print(item)
    return item


class VisualHuntResponseProcessor():
    url_template = "https://visualhunt.com/photos/key_word/index"

    @classmethod
    def parse(cls, urlTask, response):
        soup = BeautifulSoup(response,'html.parser')
        img_contents = soup.find_all(class_="vh-Collage-itemImg mini-check")


        for img_info in img_contents:
            src = img_info["data-original"]
            alt = img_info["alt"]
            item[src] = alt
        
        cur_index = int(urlTask.split("/")[-1])
        cur_key_word = urlTask.split("/")[4]

        newUrlTasks = []
        newUrlTask = cls.url_template.replace("key_word", cur_key_word).replace("index", str(cur_index+1))

        newUrlTasks.append(newUrlTask)

        return item, newUrlTasks
