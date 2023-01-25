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

user_history = ['explore']
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
    chrome.get('https://instagram.com')
    ## cookie
    cookie = {
         'name' : 'sessionid',
         "value": "57679271897%3A08nlfyeK1YV8Ph%3A29%3AAYdhVah5PVjcoVO0GGCcCsW3uz5i6uLosjvNKbCNWA"
     }
    chrome.add_cookie(cookie)
    chrome.refresh()
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
def find_p_id(chrome, id_reg="https://www.instagram.com/p/(.*)", verbose:bool=True):
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
def by_explore(chrome, scroll_times:int=10):
    if not os.path.exists(f"downloaded/instagram") : os.mkdir(f"downloaded/instagram")
    chrome.get(f"https://www.instagram.com/explore")
    time.sleep(3)
    ## get douyin.com, filter options: type=video
    for scroll in range(scroll_times):
        id_list = find_p_id(chrome)
        download(id_list, save_path=f"downloaded/instagram")
        chrome.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(4)   ## wait for webscripts ready
    return

## download video from ID recommendation recursively
def by_user(chrome, users_id:list, depth:int, verbose:bool=True):
    if verbose: print(f"[ INFO ] download by ID: Recursive-depth = {depth}")
    
    for user_id in users_id:
        chrome.get(f"https://www.instagram.com/{user_id}")
        time.sleep(2)
        chrome.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        p_list = find_p_id(chrome)
        download(p_list, save_path=f"./downloaded/instagram")
        user_history.append(user_id)

        chrome.get(f"https://www.instagram.com/{user_id}/following")
        time.sleep(2)

        new_users_id = []
        links = chrome.find_elements(by='xpath', value='//a[@href]')
        for link in links:
            text = link.get_attribute('href')
            if re.match(r'https://www.instagram.com/', text) and text[27:34] not in user_history:
                new_users_id.append(user_id)

        if depth != 0: by_user(chrome, new_users_id, depth-1)

    return 

if __name__ == "__main__":
    chrome = chrome_gen()
    #by_explore(chrome)
    by_user(chrome, ["michellewsn"], 2)
    chrome.quit()
