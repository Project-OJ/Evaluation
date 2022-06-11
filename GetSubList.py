import time
import numpy as np
import grequests
import requests
import json
import random
from urllib import response
from tqdm import tqdm

class ProgressSession():
    def __init__(self, urls):
        self.pbar = tqdm(total = len(urls), desc = 'Making async requests')
        self.urls = urls
    def update(self, r, *args, **kwargs):
        if not r.is_redirect:
            self.pbar.update()
    def __enter__(self):
        sess = requests.Session()
        sess.hooks['response'].append(self.update)
        return sess
    def __exit__(self, *args):
        self.pbar.close()

def get_urls_async(urls):
    def exception_handler(rs, error):
        url = rs.url
        print(f"{url} request failed")
        print(f"Exception: {error}")
    
    with ProgressSession(urls) as sess:
        rs = []
        for url in urls:
            rs.append(grequests.get(url, session = sess, timeout = 5))
        return grequests.map(rs, exception_handler=exception_handler)

url_sub = "https://uhunt.onlinejudge.org/api/subs-user/"
url_rk = "https://uhunt.onlinejudge.org/api/ranklist/"
uid_fname = "ac_50_data.json"
# uid_fname = "ac_100_data.json"

''' Reading uids '''
with open(uid_fname, 'r') as file:
    data = json.load(file)
    uids = [user["userid"] for user in data]

SAMPLE_SIZE = len(uids)
print(SAMPLE_SIZE)
sample_uids = uids
urls = []

for uid in sample_uids:
    urls.append(url_sub + str(uid))

url_batches = np.array_split(urls, 1)

json_data = []
with open("subs_100.json", 'w', encoding='utf-8', newline='') as outfile:
    for url_batch in url_batches:
        response = get_urls_async(url_batch)
        for r in response:
            uid = r.url.split('/')[-1]
            submissions = []
            for sub in r.json()["subs"]:
                submissions.append({
                    "submission_id": sub[0],
                    "problem_id": sub[1],
                    "verdict_id": sub[2],
                    "runtime": sub[3],
                    "submission_time": sub[4],
                })
            data = {
                "user_id": uid,
                "subs": submissions,
            }
            json_data.append(data)
        time.sleep(1)
    json.dump(json_data, outfile, indent=2)