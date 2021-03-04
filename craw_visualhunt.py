import requests
import sys
import os
import time
import json
from bs4 import BeautifulSoup

proxy = {
    'https':'https://165.22.226.8:8888'}
header = { 
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
    }

examples = [
    "https://visualhunt.com/photos/apple/2",
    "https://visualhunt.com/photos/cat/2",
    "https://visualhunt.com/photos/dog/2",
    "https://visualhunt.com/photos/love/2",
    "https://visualhunt.com/photos/people/2",
    "https://visualhunt.com/photos/techonology/2",
    "https://visualhunt.com/photos/beach/2",
    "https://visualhunt.com/photos/christmas/2",
    "https://visualhunt.com/photos/fashion/2",
    "https://visualhunt.com/photos/music/2",
    "https://visualhunt.com/photos/romance/2",
    "https://visualhunt.com/photos/travel/2",
    "https://visualhunt.com/photos/book/2",
    "https://visualhunt.com/photos/city/2",
    "https://visualhunt.com/photos/flower/2",
    "https://visualhunt.com/photos/nature/2",
    "https://visualhunt.com/photos/sea/2",
    "https://visualhunt.com/photos/tree/2",
    "https://visualhunt.com/photos/business/2",
    "https://visualhunt.com/photos/coffee/2",
    "https://visualhunt.com/photos/food/2",
    "https://visualhunt.com/photos/office/2",
    "https://visualhunt.com/photos/sky/2",
    "https://visualhunt.com/photos/women/2",
    "https://visualhunt.com/photos/car/2",
    "https://visualhunt.com/photos/computer/2",
    "https://visualhunt.com/photos/happy/2",
    "https://visualhunt.com/photos/party/2",
    "https://visualhunt.com/photos/snow/2",
    "https://visualhunt.com/photos/work/2"
]

# with open("a.txt", "w") as f:
#     for i in examples:
#         a = i.split("/")
#         f.write("'"+a[4]+"'"+", "+"\n")

key_words = [
    'apple', 
    'cat', 
    'dog', 
    'love', 
    'people', 
    'techonology', 
    'beach', 
    'christmas', 
    'fashion', 
    'music', 
    'romance', 
    'travel', 
    'book', 
    'city', 
    'flower', 
    'nature', 
    'sea', 
    'tree', 
    'business', 
    'coffee', 
    'food', 
    'office', 
    'sky', 
    'women', 
    'car', 
    'computer', 
    'happy', 
    'party', 
    'snow', 
    'work'
]

url_template = "https://visualhunt.com/photos/key_word/index"
saved_paths = []

for key_word in key_words:
    saved_path = "/media/xkx/My Passport/visualhunt/{}/".format(key_word)
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
    saved_paths.append(saved_path)

index = 1

save_path = saved_paths[0]
total_imgs = 1
while True:
    url = url_template.replace("key_word", key_words[0]).replace("index", str(index))
    response = requests.get(url, headers=header)
    page = response.text
    soup = BeautifulSoup(page,'html.parser')
    img_contents = soup.find_all(class_="vh-Collage-itemImg mini-check")

    for img in img_contents:
        alt = img["alt"]
        img_url = img["data-original"]
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