from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support import expected_conditions as EC import re
import re
import os
import time
import subprocess

## utils
def unique(x:list):
    return list(set(x))

## get a chrome driver 
def chrome_gen():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless') ## no web-gui
    chrome = webdriver.Chrome(chrome_options=chrome_options)
    return chrome

## given ['BV1MP411p75K', 'BV1vN411X75F'], download them
def download(id_list : list, save_path : str):
    for id in id_list:#[0:3]:
        cmd = ["python","-m","yutto", f"{id}"]
        cmd.extend(["-q", "127"])                                   ## quality
        cmd.extend(["--no-danmaku", "--no-subtitle", "--video-only"])
        cmd.extend(["--subpath-template",f"{id}"])
        cmd.extend(["-d", f"{save_path}"])
        cmd.extend(['-c','11b53505,1690007446,2dbb0*11'])           ## my bilibili cookie 
        subprocess.run(cmd) 
    return

def find_max_page(chrome):
    ## find max pages
    buttons = chrome.find_elements(by="xpath", value="//button")
    num_max = 1
    for button in buttons:
        try: 
            num = int(button.text)
            if num > num_max: num_max = num 
        except: continue

    return num_max

def find_video_id(chrome):
    links = chrome.find_elements(by='xpath', value="//a[@href]")
    id_list = []
    img_list = []
    for link in links:
        url = link.get_attribute('href')
        #img = link.
        ## example: https://www.bilibili.com/video/BV1vN411X75F/
        if re.match(r"https://www.bilibili.com/video/(.*)",url) is not None:
            img = link.find_element(by='xpath',value='//img[@src]')
            img_url = img.get_attribute('src')
            subprocess.run(['wget',f'{img_url}','-O', 'temp.img', '--quiet'])
            ## add some ml model for estimation of image
            img_list.append(img_url)
            id_list.append(url[31:43])

    id_list = unique(id_list)
    return id_list

def by_search(chrome,keywords:list):
    for keyword in keywords:
        if not os.path.exists(f"downloaded/{keyword}") : os.mkdir(f"downloaded/{keyword}")
        ## add filter "&duration=1", for < 10 min
        chrome.get(f"https://search.bilibili.com/all?keyword={keyword}&duration=1")
        time.sleep(3)
        num_pages = find_max_page(chrome)
        print(f"[ INFO ] Downloading all_pages={num_pages} & keyword = {keywords}")
        for page in range(1, num_pages+1):
            chrome.get(f"https://search.bilibili.com/all?keyword={keyword}&duration=1&page={page}")
            time.sleep(3)
            id_list = find_video_id(chrome)
            print(f"[ INFO ] Downloading all {len(id_list)} videos")
            print(f"[ INFO ] {id_list}") 
            download(id_list, save_path=f"downloaded/{keyword}")
        pass

## download videos from current page 

def good_face(img_path: str):
    return True

url_history = []

def by_ID(chrome, id:str, depth:int):
    chrome.get(f"https://www.bilibili.com/video/{id}") 
    time.sleep(3)
    links = chrome.find_elements(by='xpath', value="//a[@href]")

    id_list = []
    for link in links:
        url = link.get_attribute('href')
        ## example: https://www.bilibili.com/video/BV1vN411X75F/
        if re.match(r"https://www.bilibili.com/video/(.*)",url) is not None:
            img_url = link.find_element(by='xpath',value='//img[@src]').get_attribute('src')
            subprocess.run(['wget',f'{img_url}','-O', 'temp.img', '--quiet'])
            ## add some ml model for estimation of image
            if True and good_face('temp.img') and url[31:43] not in url_history :  
                id_list.append(url[31:43])

    id_list = unique(id_list)
    url_history.extend(id_list) ## avoid downloaded

    id_list = find_video_id(chrome)
    print(f"[ INFO ] Downloading all {len(id_list)} videos")
    print(f"[ INFO ] {id_list}") 
    download(id_list, save_path=f"./downloaded")

    for id in id_list:
        by_ID(chrome, id, depth-1)

    return 

### maybe some disturb
#elem = chrome.find_elements(by="xpath", value="//a[@href]")
## bilibili recommend list: "//a[@class='video-awesome-img']"
## result: href="/video/BV1MP411p75K/?spm_id_from=333.788.recommend_more_video.-1"
## preview image //picture[@class="b-img__inner"]
## ## examples
#elem[0].send_keys(Keys.TAB)
#EC.title_is(u"Baidu")(chrome)

chrome = chrome_gen()
id = 'BV1Ly4y1x7vq'
by_ID(chrome, id, 5)
chrome.quit()


chrome = chrome_gen()
id = 'BV1Ly4y1x7vq'
chrome.get(f"https://www.bilibili.com/video/{id}") 
time.sleep(3)

links = chrome.find_elements(by='xpath', value="//a[@href]")
id_list = []
for link in links:
    url = link.get_attribute('href')
    ## example: https://www.bilibili.com/video/BV1vN411X75F/
    if re.match(r"https://www.bilibili.com/video/(.*)",url) is not None:
        img_url = link.find_element(by='xpath',value='//img[@src]').get_attribute('src')
        subprocess.run(['wget',f'{img_url}','-O', 'temp.img'])
        ## add some ml model for estimation of image
        if True and good_face('temp.img'):  id_list.append(url[31:43])

id_list = unique(id_list)
id_list = find_video_id(chrome)
print(f"[ INFO ] Downloading all {len(id_list)} videos")
print(f"[ INFO ] {id_list}") 
download(id_list, save_path=f"./downloaded/begin_{id}")
#by_search(chrome, ['vlog'])
chrome.quit()
