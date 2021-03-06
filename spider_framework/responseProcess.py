import sys
sys.path.append("/home/xkx/tech-doc/spider/visual_language_dataset_spider/spider_framework/")
import json
from bs4 import BeautifulSoup


web_map = {
    0:"SearchBasedUnsplashResponseProcessor",
    1:"SearchBasedVisualHuntResponseProcessor",
    2:"RandomBasedUnsplashResponseProcessor",
}

def mongoInsert(mongoCli, dbName, cltName, item):
    collection = mongoCli[dbName][cltName]

    try:
        # item为空字典时候不添加到mongodb，但是也是请求成功的 可以删除这个url任务
        if item:
            # print("insert {} into mongodb".format(item))
            collection.insert_one(item)
    except:
        print("insert item failed")
        pass

class responseProcessRegister(object):
    _name = "responseProcessRegister"
    _obj_map = {}
    _cnt = 1

    @classmethod
    def _do_register(cls, name, obj):
        assert (
            name not in cls._obj_map
        ), "An object named '{}' was already registered in '{}' registry!".format(name, cls._name)
        cls._obj_map[name] = obj

    @classmethod
    def register(cls, obj=None):
        """
        Register the given object under the the name `obj.__name__`.
        Can be used as either a decorator or not. See docstring of this class for usage.
        """
        if obj is None:
            # used as a decorator
            def deco(func_or_class):
                name = func_or_class.__name__
                cls._do_register(name, func_or_class)
                return func_or_class

            return deco

        # used as a function call
        name = obj.__name__
        cls._do_register(name, obj)

    @classmethod
    def get(cls, name):
        ret = cls._obj_map.get(name)
        if ret is None:
            raise KeyError("No object named '{}' found in '{}' registry!".format(name, cls._name))
        return ret

    @classmethod
    def parse(cls, processorName, urlTask, text):
        return cls.get(web_map[processorName]).parse(urlTask, text)

    @classmethod
    def run(cls, redisCli, mongoCli, taskName, saveName, dbName, cltName, queReposne):
        # 从queResponse响应队列中获取响应结果
        taskNameFp = taskName + "_fp"
        while True:
            queGet = queReposne.get()
            # 结束响应处理的标志None
            if queGet is None:
                break
            urlTask, response = queGet

            # 解析网页响应结果text，
            if redisCli.hget("img_map", urlTask):
                text = redisCli.hget("img_map", urlTask)
                urlTask = urlTask.replace(".", "-")
                mongoInsert(mongoCli, dbName, cltName, {urlTask:[response, text]})
            else:
                processorName = int(redisCli.hget("task_map", urlTask))
                items, newUrlTasks = cls.parse(processorName, urlTask, response)
                # mongoInsert(mongoCli=mongoCli,dbName=dbName,item=item,cltName=cltName)
                for new_task in newUrlTasks:
                    redisCli.sadd(taskName, new_task)
                    redisCli.hset("task_map", key=new_task, value=processorName)
                    # print("add new task: {} processor_id: {}".format(new_task, processorName))
                
                for img_url in items:
                    # print(img_url, items[img_url])
                    redisCli.hset("img_text_map", key=img_url, value=items[img_url])
                    redisCli.sadd(saveName, img_url)
                
                redisCli.smove(taskName, taskNameFp, urlTask)


@responseProcessRegister.register()
class SearchBasedVisualHuntResponseProcessor():
    url_template = "https://visualhunt.com/photos/key_word/index"

    @classmethod
    def parse(cls, urlTask, response):
        item = {}
        soup = BeautifulSoup(response,'html.parser')
        img_contents = soup.find_all(class_="vh-Collage-itemImg mini-check")

        for img_info in img_contents:
            src = img_info["data-original"]
            text= img_info["alt"]
            item[src] = text
        
        cur_index = int(urlTask.split("/")[-1])
        cur_key_word = urlTask.split("/")[4]

        newUrlTasks = []
        newUrlTask = cls.url_template.replace("key_word", cur_key_word).replace("index", str(cur_index+1))

        newUrlTasks.append(newUrlTask)

        return item, newUrlTasks

@responseProcessRegister.register()
class SearchBasedUnsplashResponseProcessor():
    url_template = "https://unsplash.com/napi/topics/key_word/photos?page=index&per_page=10"

    @classmethod
    def parse(cls, urlTask, response):
        item = {}
        content_dict = json.loads(response)
        for idx in range(len(content_dict)):
            src = content_dict[idx]["urls"]["regular"]
            text = content_dict[idx]["alt_description"]
            # print(src, text)
            if text is not None:
                item[src] = text
        
        cur_index = int(urlTask.split("&per_page")[-2].split("=")[-1])
        cur_key_word = urlTask.split("/")[5]

        newUrlTasks = []
        newUrlTask = cls.url_template.replace("key_word", cur_key_word).replace("index", str(cur_index+1))

        newUrlTasks.append(newUrlTask)

        return item, newUrlTasks

@responseProcessRegister.register()
class RandomBasedUnsplashResponseProcessor():
    """
    start page: https://unsplash.com/
    """
    _start_page = "https://unsplash.com"
    @classmethod
    def parse(cls, urlTask, response):
        item = {}
        soup = BeautifulSoup(response,'html.parser')
        column_contents = soup.find_all(class_="_1ZjfQ")

        for column in column_contents:
            for img_info in column.find_all(itemprop="image"):
                # print(img_info)
                # 图片相关页面
                img_content = img_info.find(itemprop="contentUrl")
                img_related = cls._start_page + img_content["href"]
                img_src = img_content.find(class_="_2UpQX")
                if img_src is not None:
                    # 图片本身
                    src = img_src["src"]
                    # 图片alt
                    text = img_src["alt"]
                    print("img_related:{} img_src:{} text:{}".format(img_related, src, text))

        # newUrlTasks = []
        # newUrlTask = cls.url_template.replace("key_word", cur_key_word).replace("index", str(cur_index+1))

        # newUrlTasks.append(newUrlTask)

        return item, newUrlTasks


if __name__ == "__main__":
    print(responseProcessRegister.get("VisualHuntResponseProcessor"))
