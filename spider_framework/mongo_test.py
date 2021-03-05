import pymongo


mongoCli = pymongo.MongoClient(
        host="127.0.0.1",
        port=27017,
        # 实例化mongoCLi的时候，不进行链接
        connect=False,
    )


collection = mongoCli["test_mongo"]["unplash"]
item = {"aaa":"bbb"}

if item:
    print("insert {} into mongodb".format(item))
    collection.insert_one(item)

# try:
#     # item为空字典时候不添加到mongodb，但是也是请求成功的 可以删除这个url任务
#     if item:
#         print("insert {} into mongodb".format(item))
#         collection.insert_one(item)
# except:
#     print("aaaaaaaaaaaa")
#     pass
