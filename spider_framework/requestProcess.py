import os
import asyncio
import aiohttp
from selenium import webdriver
import copy
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class GetResponse():
    def __init__(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)  #设置useragent
        dcap['phantomjs.page.settings.userAgent'] = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36')  #根据需要设置具体的浏览器信息
        self._webdriver = webdriver.PhantomJS(desired_capabilities=dcap) 
        self._webdriver.set_page_load_timeout(30)

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
    
    async def phanTomjs(self, urlTask, queReposne):
        # await asyncio.sleep(1)
        print("request url:{}".format(urlTask))
        self._webdriver.get(urlTask)
        page_source = self._webdriver.page_source
        queReposne.put((urlTask, page_source))
        
        # try:
        #     print("request url:{}".format(urlTask))
        #     self._webdriver.get(urlTask)
        #     page_source = self._webdriver.page_source
        #     queReposne.put((urlTask, str(page_source)))
        # except:
        #     print("get page source failed")


async def spiderMain(*spiderS):
    await asyncio.gather(*spiderS)


def spiderEngine(queRequest, getResponse, queReposne, mode):
    """网络爬虫引擎

    """
    while True:
        # 从任务队列当中提取要爬取的url任务
        urlTaskList = queRequest.get()
        print("current request {}".format(urlTaskList))
        if urlTaskList is not None:
            # asyncio,aiohttp
            # 先构造一个并发的请求函数，为协程
            # 先定义一个并发运行协程函数的最高层级入口点
            # spiderS=[getResponse() for i in range(100)]
            if mode == "aiohttp":
                spiderS = [getResponse.aioHttpResponse(urlTask, queReposne) for urlTask in urlTaskList]
                
            elif mode == "phantomjs":
                spiderS = [getResponse.phanTomjs(urlTask, queReposne) for urlTask in urlTaskList]

            asyncio.run(spiderMain(*spiderS))
        else:
            break


async def saveResponse(redisCli, saveName, urlTask, path_to_save="/media/xkx/My Passport/spider"):
    method = "GET"
    # 加入urlTask是一个url
    # urlTask如果是一个id，我们需要构造出url
    # 比如说url=f"https://www.xxx.com/distrtct?cid={urlTask}"
    url = urlTask

    async with aiohttp.ClientSession() as ss:
        response = await ss.request(method, url)
        # print("response.status={}".format(response.status))
        if response.status == 200:
            try:
                content = await response.read()
            except:
                pass
            # print("current request {}".format(url))
            text = redisCli.hget("img_text_map", url)
            # if "unsplash" in url:
            #     text = "unsplash" + text
            # else:
            #     text = "visualhunt" + text
            path_to_save = os.path.join(path_to_save, "{}.jpg".format(text))
            with open(path_to_save,'wb') as f:
                f.write(content)
            
            redisCli.smove(saveName, saveName+"_fp", urlTask)

    # try:
    #     async with aiohttp.ClientSession() as ss:
    #         response = await ss.request(method, url)
    #         # print("response.status={}".format(response.status))
    #         if response.status == 200:
    #             text = await response.text()
    #             savedPath = os.path.join(savedPath, redisCli.hget("img_text_map", url))
    #             with open(savedPath,'wb') as f:
    #                 f.write(r.content)
    #                 f.close()
    # except:
    #     print("save image failed")

def saveImage(redisCli, saveName, saveQueRequest, saveResponse):
    """网络爬虫引擎

    """
    while True:
        # 从任务队列当中提取要爬取的url任务
        urlTaskList = saveQueRequest.get()
        # print("save image url:{}".format(urlTaskList))
        if urlTaskList is not None:
            # asyncio,aiohttp
            # 先构造一个并发的请求函数，为协程
            # 先定义一个并发运行协程函数的最高层级入口点
            # spiderS=[getResponse() for i in range(100)]
            spiderS = [saveResponse(redisCli, saveName, urlTask) for urlTask in urlTaskList]
            asyncio.run(spiderMain(*spiderS))
        else:
            break
