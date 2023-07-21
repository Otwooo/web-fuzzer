from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import tldextract
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, urlunparse
import time

options = webdriver.ChromeOptions()
# options.add_argument('headless')
driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()), options=options)

def ret_domain(url):
    extracted = tldextract.extract(url)

    subdomain = extracted.subdomain   
    domain = extracted.domain
    suffix = extracted.suffix
    return subdomain+'.'+domain+'.'+suffix

def find_subpage(target, cookies=None):

    driver.get(target)
    soup = BeautifulSoup(driver.page_source)

    print(soup)

    for link in soup.find_all('a'):            
        href = link.get('href')           

        parsed_url = urlparse(href)
        address = parsed_url.netloc
        path = parsed_url.path
        
        if address != '' and address != ret_domain(target) or href[0] == '#':                
            continue

        print(link)
        print('address :', address)     

        path = parsed_url.path
        print("path :", path)

        query_params = parsed_url.query
        print("params :", query_params)

        print("=="*20)

if __name__ == '__main__':
    attack_url = 'http://localhost:8888/wordpress/'

    find_subpage(attack_url)

driver.close()
