import requests
import sys
import os
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

proxy = {
    'https':'https://165.22.226.8:8888'}
header = { 
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
    }

def init_browser(chrome_driver="./chromedriver", proxy=None):
    browserOptions = webdriver.ChromeOptions()
    if proxy:
        browserOptions.add_argument("--proxy-server={}:{}".format(proxy["ip"], proxy["port"]))
    
    browser = webdriver.Chrome(executable_path="./chromedriver", chrome_options=browserOptions)
    time.sleep(45)
    browser.maximize_window()
    return browser

def download(broswer):
    key_word = "apple"
    search_box = broswer.find_element_by_xpath('//*[@id="search-field"]')
    search_box.send_keys(key_word)
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    cur_url = broswer.current_url()
    print(cur_url)


def main():
    key_word = ""
    root_url = "https://www.flickr.com/"
    broswer = init_browser()
    broswer.get(root_url)


if __name__ == "__main__":
    main()