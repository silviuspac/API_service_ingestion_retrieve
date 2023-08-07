import requests
from threading import *
import time

url_get = "http://localhost:8000/api/v1/retrieve"

class Ingest(Thread):
    def run(self):
        # time.sleep(0.1)
        # t1 = time.time()
        n_calls = 1000
        t1 = time.time()
        for i in range(n_calls):
            new_data = {
                "date_from": "2023-08-06 13:50:00.000Z",
                "date_to": "2023-08-09 13:50:00.000Z"
            }
            header={"x-api-key" : 'BigProfiles-API'}
            get_response = requests.get(url_get, params=new_data, headers=header)
            # get_response_json = get_response.json()
            # print(get_response_json)
        t2 = time.time()
        tot_time = (t2 - t1)
        calls_per_second = n_calls / tot_time

        print(tot_time, calls_per_second)




if __name__ == '__main__':
    num_threads = 10
    for i in range(num_threads):
        ingest_thread = Ingest()
        ingest_thread.start()