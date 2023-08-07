import requests
from threading import *
import random
import string
import time

letters = string.ascii_lowercase
url_post = "http://localhost:8000/api/v1/ingest"

class Ingest(Thread):
    def run(self):
        # time.sleep(0.1)
        t1 = time.time()
        n_calls = 1000
        for i in range(n_calls):
            key = random.randint(1, 6)

            payload_len = random.randint(10, 255)
            random_string = ''.join(random.choice(letters) for i in range(payload_len))
            new_data = {
                "key": key,
                "payload": random_string
            }
            header={"x-api-key" : 'BigProfiles-API'}
            post_response = requests.post(url_post, json=new_data, headers=header)
            # post_response_json = post_response.json()
            # print(new_data, post_response_json)
        t2 = time.time()
        tot_time = (t2 - t1)
        calls_per_second = n_calls / tot_time

        print(tot_time, calls_per_second)




if __name__ == '__main__':
    num_threads = 10
    for i in range(num_threads):
        ingest_thread = Ingest()
        ingest_thread.start()