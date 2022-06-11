from matplotlib import pyplot as plt
import math
import requests
import json

url = "https://uhunt.onlinejudge.org/api/p"

request = requests.get(url)
data = request.json()

pid_list = list()
p_array = list()

for p in data:
    if (p[3] > 3000):
        pid_list.append(p[0])
        p_array.append(p[3])

print(len(p_array)) # 553 problems that have above 3000 people that AC'ed the problem
print(max(p_array) - min(p_array))

# plt.hist(p_array, bins=200)
# plt.show()

with open("data/pid_list.json", 'w') as file:
    json.dump(pid_list, file)