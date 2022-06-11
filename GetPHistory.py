import json
from tqdm import tqdm

subs_fname = "data/subs_100.json"

# get filtered pids
with open("data/pid_list.json", 'r') as file:
    pid_list = json.load(file)

# read sampled user submissions
with open(subs_fname, 'r', encoding="utf-8") as file:
    sub_data = json.load(file)

# generate user history
uid_list = list()
p_history = dict()
for data in tqdm(sub_data, desc="generating user history"):
    uid = int(data["user_id"])
    uid_list.append(uid)
    p_history[uid] = dict()

    # sort sub_history from earliest to latest
    sub_history = sorted(data["subs"], key=lambda x : x["submission_time"])
    
    pid_set = set()
    for sub in sub_history:
        if sub["problem_id"] in pid_list:
            pid_set.add(sub["problem_id"])
    
    for pid in tqdm(pid_set, desc="processing problem record", leave=False):
        for sub in sub_history:
            if sub["problem_id"] == pid:
                if pid in p_history[uid]:
                    if p_history[uid][pid]["AC"] == False:
                        p_history[uid][pid]["attempt_cnt"] += 1
                        if sub["verdict_id"] == 90: 
                            p_history[uid][pid]["AC"] = True
                            break
                else:
                    if sub["verdict_id"] == 90:
                        p_history[uid][pid] = {
                            "AC": True,
                            "attempt_cnt": 1,
                            "solved_time": sub["submission_time"]
                        }
                        break
                    else:
                        p_history[uid][pid] = {
                            "AC": False,
                            "attempt_cnt": 1,
                            "solved_time": sub["submission_time"]
                        }
    
    p_history[uid] = dict(sorted(p_history[uid].items(), key=lambda item: item[1]["solved_time"]))

# store users problem history
with open("data/100_phistory.json", 'w') as file:
    json.dump(p_history, file, indent=2)