import redis

redisCli = redis.Redis(
        host="127.0.0.1",
        port=6379,
        db=0,
        decode_responses=True
    )

redisCli.hset("redis_test", key="aaa", value="bbb")