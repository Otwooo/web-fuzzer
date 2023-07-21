# 링크 파싱
from urllib.parse import urlparse, urlunparse, parse_qs
# 크롤링
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# time
import time
# html 파싱
from bs4 import BeautifulSoup
# 경고 제거
import warnings
warnings.filterwarnings('ignore')

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")
options.add_argument('headless') # 화면 안 보이게
driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()), options=options)

attack_domain = ""
attack_path = ""

search_page = {}

def pre_url(url): # 모든 url는 마지막에 / 가 안오도록
    if url[-1] == '/':
        url = url[0:len(url)-1]

    return url

def crawling(url):    
    driver.get(url)    
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source)
    return soup

def pre_href(now, url):    
    if urlparse(url).netloc != '': # 절대 주소, 상대 주소가 아니라면 패스
        return pre_url(url)
    else:
        if urlparse(url).path[0] == '/': # 절대 주소라면
            return urlparse(now).scheme + '://' + pre_url(attack_domain + urlparse(url).path)
        else: # 상대 주소라면                        
            index = urlparse(now).path.rfind('/')

            if '.' in urlparse(now).path[index+1:]: # now 주소가 폴더인지 파일인지                
                return now[:now.rfind('/')] + '/' + urlparse(url).path                                            
            return now + '/' + urlparse(url).path

def find_sub_page(now, text):
    sub_page = []

    for link in text.find_all('a'):
        href = link.get('href')

        if href == None or len(href) == 0 or href[0] == '#': continue # url이 #이거나 없으면 패스
        if urlparse(href).scheme != 'http' and urlparse(href).scheme != 'https' and urlparse(href).scheme != '': continue # url 스키마가 http, https가 아니면 패스        
        href = pre_href(now, href) # 절대 경로, 상대 경로 모두 도메인 붙여서 변경
                
        if urlparse(href).netloc != attack_domain: continue # 다른 도메인이면 패스
        if attack_path != '': # 만약 경로 스코프가 존재한다면 검사
            if attack_path not in urlparse(href).path: continue

        sub_page.append(href)

    return sub_page

def split_url_query(url):
    query = []    
    for i in parse_qs(urlparse(url).query):
        query.append(i)    

    url = url.replace('?' + urlparse(url).query, "")
    return pre_url(url), query

def show_info(queue, search_page):
    print("===="*20)
    print("queue :", queue)
    print('sub_page', search_page)
    print("===="*20)

def find_form_tag(now, text, queue):
    for form in text.find_all("form"):
        action = form.get("action")
        method = form.get("method")
        
        if action == None or method == None: continue
        url = now+action                 

        param_li = []
        for input_tag in form.find_all("input"):
            param = input_tag.get("name")   
            if param == None: continue                          
            
            param_li.append(param)            
        
        if url not in search_page:
            search_page[url] = [set(), set()] 
            q_url = url + '?'
            for param in param_li:
                if method == 'get':
                    search_page[url][0].update([param])
                elif method == 'post':
                    search_page[url][1].update([param])  
                q_url += param + '=temp&'
            queue.append(q_url)

def search(target, cookie=None):
    global attack_domain, attack_path, search_page

    target = pre_url(target)

    attack_domain = urlparse(target).netloc
    attack_path = urlparse(target).path
        
    print("attack_domain :", attack_domain)
    print("attack_path :", attack_path, "\n")

    search_page[target] = [set(), set()]
    queue = [target]

    while len(queue) != 0:
        show_info(queue, search_page)

        now = queue[0]
        queue.pop(0)

        html_text = crawling(now) # 셀레리움으로 html 코드 크롤링

        find_form_tag(now, html_text, queue)        
        sub_page = find_sub_page(now, html_text) # 배열로 모든 a태그 내 하위 페이지 반환

        for page in sub_page:
            pre_page, query = split_url_query(page) # 링크와 쿼리 분류, 쿼리는 배열 형태로 반환

            if pre_page not in search_page:
                queue.append(page)
                search_page[pre_page] = [set(), set()]
            search_page[pre_page][0].update(query)
    show_info(queue, search_page)    


if __name__ == '__main__':
    attack_url = 'http://localhost:8888/wordpress/'
    attack_url = 'http://localhost:8888/'
    
    search(attack_url)

    # attack_domain = "localhost:8888"    
    # print(pre_href('http://localhost:8888/wordpress', '/dd'))
    # print(pre_href('http://localhost:8888/wordpress', 'dd.html'))
    # print(pre_href('http://localhost:8888/wordpress/test.html', 'dd.html'))

    # split_url_query('http://localhost:8888/wordpress/?p=1&a=3')