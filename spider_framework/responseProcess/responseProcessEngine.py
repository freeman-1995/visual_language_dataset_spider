import sys
sys.path.append("/home/xkx/tech-doc/spider/visual_language_dataset_spider/spider_framework/")
import json
from bs4 import BeautifulSoup
from utils.registry import responseProcessor

@responseProcessor.register()
class VisualHuntResponseProcessor():
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

@responseProcessor.register()
class UnsplashResponseProcessor():
    url_template = "https://unsplash.com/napi/topics/key_word/photos?page=index&per_page=10"

    @classmethod
    def parse(cls, urlTask, response):
        item = {}
        content_dict = json.loads(response)
        for idx in range(len(content_dict)):
            src = content_dict[idx]["urls"]["regular"]
            text = content_dict[idx]["alt_description"]
            item[src] = text
        
        cur_index = int(urlTask.split("&per_page")[-2].split("=")[-1])
        cur_key_word = urlTask.split("/")[5]

        newUrlTasks = []
        newUrlTask = cls.url_template.replace("key_word", cur_key_word).replace("index", str(cur_index+1))

        newUrlTasks.append(newUrlTask)

        return item, newUrlTasks


if __name__ == "__main__":
    print(responseProcessor.get("VisualHuntResponseProcessor"))