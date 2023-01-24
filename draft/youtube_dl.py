import re
import os
import requests
from lxml import etree
import subprocess

from main import youtube_dl

proxies = {
     'http': 'http://127.0.0.1:7890',
     'https': 'http://127.0.0.1:7890',
   }


def download(id_list:list, save_path:str, proxy:str='127.0.0.1:7890'):
    for id in id_list:
        cmd = ["yt-dlp", f"{id}", "--verbose" ]
#        cmd.extend(["--proxy", f"socks5://{proxy}"]) 
        cmd.extend(["--output", f"./{save_path}/{id}"])
#        cmd.extend(["-S", "res:1080"])
        cmd.extend(['--merge-output-format', 'mp4/mkv'])
        print(cmd)
        subprocess.run(cmd)
    return;

def youtube(words:list, proxy:str="127.0.0.1:7890"):
    for word in words:
        search_url = f"https://www.youtube.com/results?search_query={word}"
        response = requests.get(search_url, proxies=proxies)
        et = etree.HTML(str(response.content,'utf-8'))
        res_str = str(et.xpath("/html/body//script[14]/text()"))
        id_list = re.findall(r'\"videoId\":\"(.*?)\"', res_str)
        id_list = list(set(id_list))        
        print(id_list)
        if not os.path.exists(f"./downloaded/youtube"): os.mkdir("./downloaded/youtube")
        if not os.path.exists(f"./downloaded/youtube/{word}"): os.mkdir(f"./downloaded/youtube/{word}")
        download(id_list, f"./downloaded/youtube/{word}")
    pass

if __name__ == "__main__":
    youtube(["vlog"])
    #download(id_list=["jEdFoYb5Ssw"], save_path="./downloaded")
    pass
