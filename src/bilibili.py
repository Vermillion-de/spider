from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support import expected_conditions as EC import re
import re
import os
import time
import subprocess

id_history = []

## utils
def unique(x:list):
    return list(set(x))

def good_face(img_path: str):    
    return True

## get a chrome driver 
def chrome_gen():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless') ## no web-gui
    chrome = webdriver.Chrome(chrome_options=chrome_options)
    return chrome

## given ['BV1MP411p75K', 'BV1vN411X75F'], download them
def download(id_list : list, save_path : str, verbose:bool = True):
    for i, id in enumerate(id_list):#[0:3]:
        if verbose: print(f"[ INFO ] Downloading {id} of task {i}/{len(id_list)}")
        cmd = ["python","-m","yutto", f"{id}"]
        cmd.extend(["-q", "127"])                                   ## quality
        cmd.extend(["--no-danmaku", "--no-subtitle", "--video-only"])
        cmd.extend(["--subpath-template",f"{id}"])
        cmd.extend(["-d", f"{save_path}"])
        cmd.extend(['-c','11b53505,1690007446,2dbb0*11'])           ## my bilibili cookie 
        subprocess.run(cmd) 
        id_history.append(id)
    return

## find max pages of current webpage
def find_max_page(chrome):
    buttons = chrome.find_elements(by="xpath", value="//button")
    num_max = 1
    for button in buttons:
        try: 
            num = int(button.text)
            if num > num_max: num_max = num 
        except: continue
    return num_max

## download videos from current page 
def find_video_id(chrome, id_reg="https://www.bilibili.com/video/(.*)",verbose:bool = True):
    links = chrome.find_elements(by='xpath', value="//a[@href]")
    id_img_list = [] ## the pair for [(id, img)]
    
    ## summarized all links
    for link in links:
        id_url = link.get_attribute('href')
        if re.match(id_reg,id_url) is not None:
            img_url = link.find_element(by='xpath',value='//img[@src]').get_attribute('src')
            id_img_list.append((id_url[31:43], img_url))  
    id_img_list = unique(id_img_list)
    if verbose: print(f"[ INFO ] All {len(id_img_list)} videos for found")

    id_list = []
    for (id, img_url) in id_img_list:
        if verbose: print(f"[ INFO ] downloading and testing img for {id}...")
        subprocess.run(['wget',f'{img_url}','-O', f'./imgs/{id}.img', '--quiet'])
        if good_face("temp.img") and id not in id_history: 
            id_list.append(id)
    
    if verbose: print(f"[ INFO ] Will download video_id: {id_list}")
    return id_list

## scrape video by search
def by_search(chrome,keywords:list):
    for keyword in keywords:
        if not os.path.exists(f"downloaded/{keyword}") : os.mkdir(f"downloaded/{keyword}")
        ## add filter "&duration=1", for < 10 min
        chrome.get(f"https://search.bilibili.com/all?keyword={keyword}&duration=1")
        time.sleep(2)   ## wait for webscripts ready
        num_pages = find_max_page(chrome)
        print(f"[ INFO ] Downloading pages={num_pages}&keyword={keywords}")

        for page in range(1, num_pages+1):
            chrome.get(f"https://search.bilibili.com/all?keyword={keyword}&duration=1&page={page}")
            time.sleep(2)
            id_list = find_video_id(chrome)
            download(id_list, save_path=f"downloaded/{keyword}")

        return

## download video from ID recommendation recursively
def by_ID(chrome, id_list:list, depth:int, verbose:bool=True):
    if verbose: print(f"[ INFO ] download by ID: Recursive-depth = {depth}")
    download(id_list, save_path=f"./downloaded/")
    for id in id_list:
        chrome.get(f"https://www.bilibili.com/video/{id}") 
        time.sleep(2)
        id_list = find_video_id(chrome)
        by_ID(chrome, id_list, depth-1)
    return 

### maybe some disturb
#elem = chrome.find_elements(by="xpath", value="//a[@href]")
## bilibili recommend list: "//a[@class='video-awesome-img']"
## result: href="/video/BV1MP411p75K/?spm_id_from=333.788.recommend_more_video.-1"
## preview image //picture[@class="b-img__inner"]
## ## examples
#elem[0].send_keys(Keys.TAB)
#EC.title_is(u"Baidu")(chrome)

if __name__ == "__main__":
    chrome = chrome_gen()
    #id_list = ['BV1Ly4y1x7vq']
    #by_ID(chrome, id_list, 3)
    by_search(chrome, ['vlog'])
    chrome.quit()
