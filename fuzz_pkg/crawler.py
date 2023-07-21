import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import tldextract
from urllib.parse import urlparse, urlunparse

subpage = {'/':[]}

def ret_domain(url):
    extracted = tldextract.extract(url)

    subdomain = extracted.subdomain   
    domain = extracted.domain
    suffix = extracted.suffix
    return subdomain+'.'+domain+'.'+suffix

def find_subpage(target, cookies=None):

    res = requests.get(target, cookies=cookies)
    soup = BeautifulSoup(res.text, 'html.parser')    

    print(res.text)

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

    # print(res.url)    
    # print(res.headers)
    # print(res.text)


if __name__ == '__main__':
    attack_url = 'https://minelist.kr/'

    find_subpage(attack_url)        