from fuzz_pkg.crawler import search
import sys
from fuzz_pkg.worker import worker_GET

import sys

if len(sys.argv) < 3:   
    print("main.py {attack_url} {attack_type} {attack_time=60} 형식으로 입력해주세요")

attack_url = sys.argv[1]
attack_type = sys.argv[2]

if len(sys.argv) >= 4 :
    attack_time = sys.argv[3]
    search(attack_url, t=attack_time)
else:
    search(attack_url)
worker_GET(attack_url, 'xss')

# attack_url = 'http://localhost:8888/test/'
# search(attack_url, t=180)