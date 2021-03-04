import requests
import sys
import os
import time
import json

proxy = {
    'https':'https://165.22.226.8:8888'}
header = { 
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
    }

examples = [
    "https://unsplash.com/napi/topics/color-theory/photos?page=5&per_page=10",
    "https://unsplash.com/napi/topics/wallpapers/photos?page=5&per_page=10",
    "https://unsplash.com/napi/topics/nature/photos?page=5&per_page=10",
    "https://unsplash.com/napi/topics/people/photos?page=5&per_page=10",
    "https://unsplash.com/napi/topics/architecture/photos?page=5&per_page=10",
    "https://unsplash.com/napi/topics/current-events/photos?page=6&per_page=10",
    "https://unsplash.com/napi/topics/business-work/photos?page=4&per_page=10",
    "https://unsplash.com/napi/topics/experimental/photos?page=5&per_page=10",
    "https://unsplash.com/napi/topics/fashion/photos?page=1&per_page=20",
    "https://unsplash.com/napi/topics/film/photos?page=1&per_page=20",
    "https://unsplash.com/napi/topics/health/photos?page=3&per_page=10",
    "https://unsplash.com/napi/topics/interiors/photos?page=1&per_page=20",
    "https://unsplash.com/napi/topics/street-photography/photos?page=4&per_page=10",
    "https://unsplash.com/napi/topics/technology/photos?page=4&per_page=10",
    "https://unsplash.com/napi/topics/travel/photos?page=4&per_page=10",
    "https://unsplash.com/napi/topics/textures-patterns/photos?page=4&per_page=10",
    "https://unsplash.com/napi/topics/animals/photos?page=3&per_page=10",
    "https://unsplash.com/napi/topics/food-drink/photos?page=3&per_page=10",
    "https://unsplash.com/napi/topics/athletics/photos?page=4&per_page=10",
    "https://unsplash.com/napi/topics/spirituality/photos?page=5&per_page=10",
    "https://unsplash.com/napi/topics/arts-culture/photos?page=5&per_page=10",
    "https://unsplash.com/napi/topics/history/photos?page=5&per_page=10"
]
key_words = [
    "color-theory",
    "wallpapers",
    "nature",
    "people",
    "architecture",
    "current-events",
    "business-work",
    "experimental",
    "fashion",
    "film",
    "health",
    "interiors",
    "street-photography",
    "technology",
    "travel",
    "textures-patterns",
    "animals",
    "food-drink",
    "athletics",
    "spirituality",
    "arts-culture",
    "history"
]

url_template = "https://unsplash.com/napi/topics/key_word/photos?page=index&per_page=10"
saved_paths = []

for key_word in key_words:
    saved_path = "/media/xkx/My Passport/unsplash/{}/".format(key_word)
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
    saved_paths.append(saved_path)

index = 1

save_path = saved_paths[0]
total_imgs = 1
while True:
    url = url_template.replace("key_word", key_words[0]).replace("index", str(index))
    response = requests.get(url, headers=header)
    content_dict = json.loads(response.content.decode())

    for idx in range(len(content_dict)):
        img_url = content_dict[idx]["urls"]["regular"]
        img_res = requests.get(img_url, headers=header)
        if img_res.status_code==200:
            img_path = os.path.join(save_path, "{}.jpg".format(total_imgs))
            print("save img {}.jpg".format(total_imgs))
            with open(img_path,'wb') as f:
                f.write(img_res.content)
                time.sleep(1)
                f.close()
            total_imgs += 1

    index += 1
    if index == 10:
        exit()