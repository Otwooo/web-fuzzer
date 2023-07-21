import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import tldextract
from urllib.parse import urlparse, urlunparse
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import warnings
import time
warnings.filterwarnings('ignore')


subpage = {}

def find_subpage(target, cookies=None):
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")
    options.add_argument('headless') # 화면 안 보이게
    driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()), options=options)
    

    print("crawling", target + "...")
    print("")

    if target[-1] == '/':
        target = target[0:len(target)-1]        
    subpage[target] = []

    queue = ['/']
    
    while len(queue) != 0:         

        print("==="*20)
        print("queue :", queue)
        print("==="*20)
        print("subpage :", subpage)
        print("==="*20)
        now = target + queue[0]
        driver.get(now)
        
        # 다 로딩되기까지 기다림
        time.sleep(5)

        queue.pop(0)
        
        soup = BeautifulSoup(driver.page_source)          

        for link in soup.find_all('a'):
            href = link.get('href')            
            if href == None: continue                                                    
            if urlparse(href).scheme != 'http' and urlparse(href).scheme != 'https' and urlparse(href).scheme != '':
                continue

            if urlparse(href).netloc == '':                
                if urlparse(href).path == '':                 
                    continue

                parse = urlparse(target)
                temp = parse.scheme + "://" + parse.netloc

                if urlparse(href).path[0] != '/':
                    if '.php' in now or '.html' in now:
                        index = now.rfind('/')
                        url = now[:index]
                    href = url + '/' + urlparse(href).path
                else:
                    href = temp + urlparse(href).path

            parsed_url = urlparse(href)
            address = parsed_url.netloc # 도메인 파싱               

            if target in href: # 같은 도메인일 때만 
                parse = urlparse(href)
                print(parse)
                damain_path = parse.scheme + "://" + parse.netloc + parse.path

                if damain_path[-1] == '/':
                    damain_path = damain_path[0:len(damain_path)-1]  

                if damain_path not in subpage:
                    queue.append(parse.path)
                    subpage[damain_path] = []

    # driver.close()

if __name__ == '__main__':
    attack_url = 'http://localhost:8888/wordpress/' # 입력값으로 하위 페이지를 넣어도 된다. 단 파라미터를 포함시키지는 말아야한다. 하위  페이지로 넣
    # attack_url = 'http://localhost:8888/test/'
    # attack_url = 'https://www.naver.com/'

    find_subpage(attack_url)
    print(subpage)


# 파라미터가 다른게 있으면 또 요청해야함.