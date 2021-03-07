import aiohttp
import asyncio
from selenium import webdriver
import multiprocessing

class GetResponse():
    def __init__(self):
        self._webdriver = webdriver.PhantomJS()

    async def aioHttpResponse(self, urlTask, queReposne):
        method = "GET"
        # 加入urlTask是一个url
        # urlTask如果是一个id，我们需要构造出url
        # 比如说url=f"https://www.xxx.com/distrtct?cid={urlTask}"
        url = urlTask

        # async with aiohttp.ClientSession() as ss:
        #     response = await ss.request(method, url)
        #     # print("response.status={}".format(response.status))
        #     if response.status == 200:
        #         text = await response.text()
        #         # 需要有错误处理机制，可以首先根据响应码来判断是否为200
        #         queReposne.put((urlTask, text))

        try:
            async with aiohttp.ClientSession() as ss:
                response = await ss.request(method, url)
                # print("response.status={}".format(response.status))
                if response.status == 200:
                    text = await response.text()
                    # 需要有错误处理机制，可以首先根据响应码来判断是否为200
                    queReposne.put((urlTask, text))
        except:
            print("anysc request failed")
    
    async def phanTomjs(self, urlTask, queRequest):
        await asyncio.sleep(1)
        print("request url:{}".format(urlTask))
        self._webdriver.get(urlTask)
        
        page_source = self._webdriver.page_source
        queRequest.put((urlTask, page_source))
        
        # try:
        #     self._webdriver.get(urlTask)
        #     page_source = self._webdriver.page_source()
        #     queReposne.put((urlTask, page_source))
        # except:
        #     print("get page source failed")


async def spiderMain(*spiderS):
    await asyncio.gather(*spiderS)


def spiderEngine(getResponse, urlTaskList, queRequest):
    """网络爬虫引擎

    """
    while True:
        if urlTaskList is not None:
            spiderS = [getResponse.phanTomjs(urlTask, queRequest) for urlTask in urlTaskList]
            asyncio.run(spiderMain(*spiderS))
        else:
            break


urlTaskList = ["https://unsplash.com/photos/m4_W2390DSI"]
queRequest = multiprocessing.Queue(maxsize=2000)
pList = [multiprocessing.Process(
        target=spiderEngine, args=(GetResponse(), urlTaskList, queRequest), name=f'{i}') for i in range(1)]

[p.start() for p in pList]
