import  redis

redisCli=redis.Redis(host="127.0.0.1",port=6379,db=2)
taskName="get-cid"
ditrictList = ["dc", "ft", "dx", "my", "pg", "yq",
               "hr", "fs", "cp", "cy", "hd", "sjs",
               "xc", "tz", "mtg", "sy"]
for d in ditrictList:
    # d:代表地区， 0 代表skip
    urlTask=f"{d}__0"
    redisCli.sadd(taskName,urlTask)