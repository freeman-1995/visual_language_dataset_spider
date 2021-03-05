import asyncio


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
        else:
            break