import asyncio


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