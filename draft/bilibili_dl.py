from time import sleep
import requests
import subprocess
from lxml import etree
import os

def download(id_list : list, save_path : str):
    for id in id_list:
        cmd = ["python","-m","yutto", f"{id}"]
        cmd.extend(["-q", "127"])
        cmd.extend(["--no-danmaku", "--no-subtitle", "--video-only"])
        cmd.extend(["--subpath-template",f"{id}"])
        cmd.extend(["-d", f"{save_path}"])
        cmd.extend(['-c','11b53505,1690007446,2dbb0*11'])
        subprocess.run(cmd)
    pass

def bilibili(words : list, save_path : str):
    head ={ 'User_Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36' } 
    for word in words:
        if not os.path.exists(f"{save_path}/{word}") : os.mkdir(f"{save_path}/{word}")
        response = requests.get(f"https://search.bilibili.com/all?keyword={word}", headers=head)
        print("[ INFO ] Status Code: ", response.status_code)
        et = etree.HTML(str(response.content, 'utf-8'))
        page = et.xpath("//button/text()")
        num_pages = int(page[-2])

        for page in range(1,num_pages+1):
            if not os.path.exists(f"{save_path}/{word}/{page}") : os.mkdir(f"{save_path}/{word}/{page}")
            print(f"[ INFO ] Getting page {page}")
            response = requests.get(f"https://search.bilibili.com/all?keyword={word}&page={page}")
            et = etree.HTML(str(response.content, 'utf-8'))
            links = et.xpath("//a[@class='img-anchor']/@href")
            if (len(links) == 0): break
            for link in links:
                download([link[25:37]], save_path=f"{save_path}/{word}/{page}")
            sleep(1)

def main(url_list):
    download(url_list, "./downloaded/")
    pass

if __name__ == "__main__":
    id_list = bilibili(words=["采访"],save_path="/home/chi/downloaded")
    print(id_list)
   # download(id_list,"./downloaded/")
    pass

