import time
import requests

URL = "http://localhost:8000/"  # or nginx:80 after Nginx setup
NUM_REQUESTS = 100

times = []

for i in range(NUM_REQUESTS):
    start = time.time()
    r = requests.get(URL)
    r.raise_for_status()  # ensures it succeeded
    end = time.time()
    times.append(end - start)

avg_time = sum(times) / len(times)
print(f"Average response time over {NUM_REQUESTS} requests: {avg_time*1000:.2f} ms")