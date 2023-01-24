from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

## get a chrome driver 
proxy = "127.0.0.1:7890"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'--proxy-server={proxy}')
#chrome_options.add_argument('--headless') ## no web-gui
chrome = webdriver.Chrome(chrome_options=chrome_options)


## add &sp=EgIYAQ%253D%253D for filter
## get instagram website and analysis for xpath
chrome.get("https://instagram.com")
cookie = {
        "name"  : "sessionid",
        "value" : "57679271897%3A08nlfyeK1YV8Ph%3A29%3AAYedlGmPGu9ZZqdI22Erzq8fcDXJRT0lvN_D4Kpm3A"
}
chrome.add_cookie(cookie)
chrome.refresh()
## maybe do something
links = chrome.find_elements(by='xpath', value="//a[@href]")
id_list = []
for link in links:
    id_list.append(link.get_attribute('href'))

print(id_list)

### maybe some disturb
elem = chrome.find_elements(by="xpath", value="//a[@href]")

## examples
elem[0].send_keys(Keys.TAB)
EC.title_is(u"Baidu")(chrome)





chrome.quit()
