def redisRun(redisCli, taskName, concurrentCount, queRequest, mulProNums):
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
            # print(urlTaskList)
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
