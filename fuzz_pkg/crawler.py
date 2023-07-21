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
# csv
import csv

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")
options.add_argument('headless') # 화면 안 보이게
driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()), options=options)

attack_domain = ""
attack_path = ""

search_page = {}

def pre_url(url): # 모든 url는 마지막에 / 가 안오도록    
    if url[-1] == '?':
        url = url[0:len(url)-1]
    if url[-1] == '/':
        url = url[0:len(url)-1]

    return url

def crawling(url, cookie=None):    
    driver.get(url)
    if cookie != None:
        driver.add_cookie(cookie)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source)
    return soup

def pre_href(now, url):
    if len(url) == 0:
        return now

    if url[0] == '?':
        return now + url

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
    print('sub_page', search_page)
    # print('queue :', queue)
    print("===="*20)

def find_form_tag(now, text, queue):
    for form in text.find_all("form"):
        action = form.get("action")
        method = form.get("method")
        
        if action == None or method == None: continue
        url = pre_href(now, action)

        if pre_url(url) not in search_page:
            search_page[pre_url(url)] = [set(), set()] 
            queue.append(pre_url(url))
                
        for input_tag in form.find_all("input"):
            param = input_tag.get("name")   
            if param == None: continue                          
            
            if method == 'get':
                    search_page[pre_url(url)][0].update([param])
            elif method == 'post':
                search_page[pre_url(url)][1].update([param])

def save(page, target):
    name = urlparse(target).netloc.replace('.', '') + urlparse(target).path.replace('.', '')
    name = name.replace('/', '')
    with open(f'./data/{name}.csv', 'w', newline='') as file:
        fieldnames = ['url', 'get_method', 'post_method']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for url in page:
            get_method = ', '.join(get_params for get_params in page[url][0] )
            post_method = ', '.join(post_params for post_params in page[url][1])
            writer.writerow({'url': url, 'get_method': get_method, 'post_method': post_method})


def search(target, cookie=None, t=60):
    desired_time = time
    global attack_domain, attack_path, search_page, driver    

    target = pre_url(target)

    attack_domain = urlparse(target).netloc
    attack_path = urlparse(target).path
        
    print("attack_domain :", attack_domain)
    print("attack_path :", attack_path, "\n")

    search_page[pre_url(target)] = [set(), set()]
    queue = [target]

    # 60초가 지나면 자동으로 크롤링이 종류되도록
    start_time = time.time()
    while len(queue) != 0:
        show_info(queue, search_page)

        now = queue[0]
        queue.pop(0)

        # 가끔 에러가 발생해서 에러가 발생하면 그냥 넘어가도록
        # try:
        html_text = crawling(now, cookie) # 셀레리움으로 html 코드 크롤링
        # except:
            # print(f"error with {now}")
            # continue

        find_form_tag(now, html_text, queue) # from 태그를 파싱해서 새로운 주소라면 큐랑 데이터에 추가해주고 쿼리도 모두 추가        
        sub_page = find_sub_page(now, html_text) # 배열로 모든 a태그 내 하위 페이지 반환
                
        for page in sub_page:
            pre_page, query = split_url_query(page) # 링크와 쿼리 분류, 쿼리는 배열 형태로 반환

            if target not in page: continue

            if pre_url(pre_page) not in search_page:
                queue.append(page)
                search_page[pre_url(pre_page)] = [set(), set()]
            search_page[pre_url(pre_page)][0].update(query)

        if time.time() - start_time >= desired_time:
            print(f'{desired_time}seconds have passed. -> break') 
            break

    show_info(queue, search_page)
    save(search_page, target)


if __name__ == '__main__':
    attack_url = 'http://localhost:8888/wordpress/'        
    attack_url = 'https://www.hackthissite.org/'
    search(attack_url, t=180)

    # attack_url = 'http://localhost:8888/wordpress/wp-admin/'
    # search(attack_url, {'name':'wordpress_2b7738476b2cfaf3b5454b1e89821e63', 'value':'admin%7C1690131873%7CmBcFL64SqW4eLKcvCasHEZNVUn2UR5tSlMbXXp0aR0Q%7C4b1cd784c4ad1a212df11ec2c978eb6afb2e2dafb62a4fde6a4dc45d51d39068'}, 180)

    # 쿼리가 달라지거나 추가된다고 모두 탐색하지 않음 이걸 추가해야하나? 귀찮은데