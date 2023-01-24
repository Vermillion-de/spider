from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support import expected_conditions as EC
import re
import subprocess

def unique(x:list):
    return list(set(x))

def download(id_list : list, save_path : str):
    for id in id_list:
        cmd = ["python","-m","yutto", f"{id}"]
        cmd.extend(["-q", "127"])
        cmd.extend(["--no-danmaku", "--no-subtitle", "--video-only"])
        cmd.extend(["--subpath-template",f"{id}"])
        cmd.extend(["-d", f"{save_path}"])
        cmd.extend(['-c','11b53505,1690007446,2dbb0*11']) 
        subprocess.run(cmd) 
    return

## get a chrome driver 
def chrome_gen():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless') ## no web-gui
    chrome = webdriver.Chrome(chrome_options=chrome_options)
    return chrome


chrome = chrome_gen()

## get instagram website and analysis for xpath
keyword = "BBC"
chrome.get(f"https://search.bilibili.com/all?keyword={keyword}")
## add filter "&duration=1", for < 10 min

## maybe do something
links = chrome.find_elements(by='xpath', value="//a[@href]")

id_list = []
for link in links:
    url = link.get_attribute('href')
    ## example: https://www.bilibili.com/video/BV1vN411X75F/
    if re.match(r"https://www.bilibili.com/video/(.*)",url) is not None:
        id_list.append(url[31:43])

id_list = unique(id_list)

print(id_list)
print(len(id_list))

download(id_list, save_path="downloaded")
### maybe some disturb
#elem = chrome.find_elements(by="xpath", value="//a[@href]")
## bilibili recommend list: "//a[@class='video-awesome-img']"
## result: href="/video/BV1MP411p75K/?spm_id_from=333.788.recommend_more_video.-1"
## preview image //picture[@class="b-img__inner"]
## ## examples
#elem[0].send_keys(Keys.TAB)
#EC.title_is(u"Baidu")(chrome)
chrome.quit()
