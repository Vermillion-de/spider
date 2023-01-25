from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support import expected_conditions as EC import re
import re
import os
import time
import subprocess

import io
from PIL import Image
import base64  

user_history = []
id_history = []
proxy='127.0.0.1:7890'
env = os.environ.copy()
env.update({
    'http_proxy' : proxy,
    'https_proxy' : proxy
})

## utils
def unique(x:list):
    return list(set(x))

def save_base64(img_bs64:str, save_path:str):
    img = Image.open(io.BytesIO(base64.decodebytes(bytes(img_bs64,'utf-8'))))
    img.save(f'{save_path}')
    pass

def good_face(img_path: str):    
    return True

## get a chrome driver 
def chrome_gen(proxy:str='127.0.0.1:7890'):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--proxy-server={proxy}')
    chrome = webdriver.Chrome(chrome_options=chrome_options)
    chrome.get('https://youtube.com')
    ## cookie = {}
    #chrome.add_cookie(cookie)
    #chrome.refresh()
    return chrome

## given: id_list ['1287832478203748213'], save_path="./downloaded/tiktok/" 
def download(id_list:list, save_path:str, cookie_path:str="./cookies/tiktok.cookie",verbose:bool = True, proxy:str="127.0.0.1:7890"):
    for i, id in enumerate(id_list):#[0:3]:
        if verbose: print(f"[ INFO ] Downloading {id} of task {i}/{len(id_list)}")
        cmd = ["instaloader", "--", f"-{id}"]
        #cmd.extend(["--output", f"{save_path}/{id}"])
        #cmd.extend(["-S", "res:480"])                                   ## quality
        #cmd.extend(['--external-downloader','aria2c'])
        # cmd.extend(["--no-danmaku", "--no-subtitle", "--video-only"])
        if id in id_history: continue 
        subprocess.run(cmd,env=env) 
        id_history.append(id)
    return


## download videos from current page 
def find_video_id(chrome, id_reg="https://www.instagram.com/p/(.*)", verbose:bool=True):
    links = chrome.find_elements(by='xpath', value="//a[@href]")
    id_img_list = [] ## the pair for [(id, img)]
    ## summarized all links
    for link in links:
        id_url = link.get_attribute('href')
        if re.match(id_reg,id_url) is not None:
            img_url = link.find_element(by='xpath',value='//img[@src]').get_attribute('src')
            id_img_list.append((id_url[28:39], img_url))  
    id_img_list = unique(id_img_list)
    if verbose: print(f"[ INFO ] All {len(id_img_list)} pages for found")
    id_list = []
    for (id, img_bs64) in id_img_list:
        if verbose: print(f"[ INFO ] downloading and testing img id={id}")
        ## instagram use base64 encoding for imgs
        save_base64(img_bs64[22:], f'./imgs/{id}.png')
        #subprocess.run(['wget',f'{img_url}','-O', f'./imgs/{id}.img', '--quiet'], env=env)
        if good_face("temp.img") and id not in id_history: 
            id_list.append(id)
    if verbose: print(f"[ INFO ] Will download video_id: {id_list}")
    return id_list

## scrape video by search
def by_search(chrome,keywords:list, scroll_times:int=3):
    for keyword in keywords:
        if not os.path.exists(f"downloaded/{keyword}") : os.mkdir(f"downloaded/{keyword}")
        chrome.get(f"https://douyin.com/search/{keyword}?type=video")
        time.sleep(3)
        ## get douyin.com, filter options: type=video
        for scroll in range(scroll_times):
            id_list = find_video_id(chrome)
            download(id_list, save_path=f"downloaded/tiktok/{keyword}")
            chrome.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(4)   ## wait for webscripts ready
        return

## download video from ID recommendation recursively
def by_ID(chrome, id_list:list, depth:int, verbose:bool=True):
    if verbose: print(f"[ INFO ] download by ID: Recursive-depth = {depth}")
    download(id_list, save_path=f"./downloaded/tiktok/")
    for id in id_list:
        chrome.get(f"https://www.douyin.com/video/{id}") 
        time.sleep(2)
        id_list = find_video_id(chrome)
        if id_list == []: input("Please Verficate it...")
        if depth != 0 : 
            by_ID(chrome, id_list, depth-1)
    return 

if __name__ == "__main__":
    chrome = chrome_gen()
    #by_explore(chrome)
    by_search(chrome,["vlog"])
    chrome.quit()
