import json
import random
from RSEvaluator import RSEvaluator

class RandomRS:
    def __init__(self):
        with open("data/pid_list.json", 'r') as file:
            self.pid_list = json.load(file)
    
    def getRecom(self, sim_ph):
        return random.sample(self.pid_list, 50)

if __name__ == "__main__":
    rs = RandomRS()
    rse = RSEvaluator("data/100_phistory.json", rs, ppr=1000, sim_init_length=10)
    result = rse.simulate()