import streamlit as st
import requests
from lxml import etree
import re


proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}


url = st.text_input(
        "URL of the website",
        "https://www.youtube.com/results?search_query=fake+love+orchestra"
      )

xpath = st.text_input(
        "Xpath of your research",
        "/html/body//script[14]/text()"
    )

if url and xpath:
    response = requests.get(url, proxies=proxies)
    et = etree.HTML(str(response.content,'utf-8'))
    results = et.xpath(xpath)
    st.write("url: ", url)
    st.write("xpath is ",xpath)
    st.write("all ", len(results), )
    res_str = str(results[0])
    st.write(len(res_str))
    matchobj = re.findall(r'\"videoId\":\"(.*?)\"', res_str)
    matchobj = list(set(matchobj))
    st.write(matchobj)

    #st.write(results[-2])
    #for i, res in enumerate(results):
    #    st.write(res, f" No. {i}")
    #    st.write(str(etree.tostring(res,encoding="utf-8"),'utf-8'))
    #pass


