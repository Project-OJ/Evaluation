import json
import random
from RSEvaluator import RSEvaluator

class RandomRS:
    def __init__(self):
        with open("data/pid_list.json", 'r') as file:
            self.pid_list = json.load(file)
    
    def getRankList(self, sim_ph):
        return random.sample(self.pid_list, len(self.pid_list))

if __name__ == "__main__":
    rs = RandomRS()

    # Evaluate users with 50 AC's
    # rse = RSEvaluator("data/50_phistory.json", rs, ppr=1000, sim_init_length=10)
    # Evaluate users with 100 AC's

    # The default ppr (problem per round) is set to 10
    # set it to something like 5000 to get the entire problem history in one round
    # sim_init_length is the length of the problem history for you to initialize your recommender system
    rse = RSEvaluator("data/100_phistory.json", rs, ppr=5, sim_init_length=10)
    result = rse.simulate()
    print(json.dumps(result, indent=2))