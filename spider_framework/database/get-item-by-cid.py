import  redis
import  pymongo
mongoCLi=pymongo.MongoClient(
    host="127.0.0.1",port=27017,
)
redisCli=redis.Redis(
    host="127.0.0.1",port=6379,
    db=2
)
clt=mongoCLi['51zxw-company']['all-cid']
cursor=clt.find()
taskName="get-item"
def main():
    for i in cursor:
        urlTask = i["_id"]
        redisCli.sadd(taskName, urlTask)
        # return

if __name__ == '__main__':
    main()
