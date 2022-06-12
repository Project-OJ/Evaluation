import json
import csv
import random
from tqdm import tqdm

class BuildUPMatrix:
    def __init__(self, subs_fname, pid_list_fname):
        self.problem_history = dict()
        self.uid_list = list()
        self.problem_info = dict()
        self.tt_dict = dict()
        self.problem_history_bp = dict()
        self.submissions_fname = subs_fname
        with open(pid_list_fname, 'r') as file:
            self.pid_list = json.load(file)
            self.pid_list.insert(0, "uid")
    
    def generate_problem_history(self):
        # read sampled user submissions
        with open(self.submissions_fname, 'r', encoding="utf-8") as submission_file:
            submission_data = submission_file.read()

        # parse submissions
        json_data = json.loads(submission_data)

        # generate user history
        for data in tqdm(json_data, desc="generating user history"):
            uid = int(data["user_id"])
            self.uid_list.append(uid)
            self.problem_history[uid] = dict()

            sub_history = sorted(data["subs"], key=lambda x : x["submission_time"], reverse=True)
            
            pid_set = set()

            for sub in sub_history:
                pid_set.add(sub["problem_id"])
            
            for pid in tqdm(pid_set, desc="processing problem record", leave=False):
                solved_attempt_sum = 0
                unsolved_attempt_sum = 0
                solved_user_sum = 0
                unsolved_user_sum = 0
                for sub in sub_history:
                    if sub["problem_id"] == pid:
                        if pid in self.problem_history[uid]:
                            if self.problem_history[uid][pid]["isSolved"] == True:
                                if sub["verdict_id"] == 90:
                                    break
                                else:
                                    self.problem_history[uid][pid]["attemptCnt"] += 1
                        else:
                            if sub["verdict_id"] == 90:
                                self.problem_history[uid][pid] = {
                                    "isSolved": True, 
                                    "attemptCnt": 1, 
                                    "solvedTime": sub["submission_time"]
                                }
                            else:
                                self.problem_history[uid][pid] = {
                                    "isSolved": False, 
                                    "attemptCnt": 1, 
                                    "solvedTime": sub["submission_time"]
                                }
                
                if self.problem_history[uid][pid]["isSolved"] == True:
                    solved_user_sum += 1
                    solved_attempt_sum += self.problem_history[uid][pid]["attemptCnt"]
                else:
                    unsolved_user_sum += 1
                    unsolved_attempt_sum += self.problem_history[uid][pid]["attemptCnt"]
                
                self.problem_info[pid] = {"solved_user_sum": solved_user_sum, "solved_attempt_sum": solved_attempt_sum,
                                    "unsolved_user_sum": unsolved_user_sum, "unsolved_attempt_sum": unsolved_attempt_sum}

        self.problem_history_bp = self.problem_history.copy()
        user_problem_history_string = json.dumps(self.problem_history)

        # store users' problem history
        with open("CFRS_data/p_history_100.json", 'w') as file:
            file.write(user_problem_history_string)
        
        with open("CFRS_data/p_info_100.json", 'w') as file:
            json.dump(self.problem_info, file, indent=2)
    
    def generate_tt_set(self):
        p_sum = 0.0
        ac_list = []
        cnt = 0.0
        for uid in self.uid_list:
            pid_keys = self.problem_history[uid].keys()
            pid_list = list()
            for key in pid_keys:
                if self.problem_history[uid][key]["isSolved"] == True: pid_list.append(key)
            p_sum += len(pid_list)
            if len(pid_list) > 0: cnt += 1
            ac_list.append(len(pid_list))
            random.shuffle(pid_list)
            training_set = pid_list[:int(len(pid_list)/2)]
            test_set = pid_list[int(len(pid_list)/2):]
            self.tt_dict[uid] = (training_set, test_set)

    def prepare_test(self, test_uid):
        print(self.tt_dict[test_uid][0])
        print(self.tt_dict[test_uid][1])
        for test_pid in self.tt_dict[test_uid][1]:
            for pid in self.problem_history[test_uid]:
                if test_pid == pid:
                    self.problem_history[test_uid].pop(pid)
                    break
    
    def restore_problem_history(self):
        self.problem_history = self.problem_history_bp.copy()

    def generate_up_matrix(self):
        with open("CFRS_data/up_matrix_100.csv", 'w', encoding='UTF8', newline='') as file:
            writer = csv.writer(file)

            # wirte the header
            writer.writerow(self.pid_list)

            # write data
            for uid in tqdm(self.uid_list, desc="generating UP matrix"):
                data_list = [uid]
                for pid in self.pid_list[1:]:
                    if pid in self.problem_history[uid]:
                        lambda1 = self.problem_info[pid]["unsolved_attempt_sum"] / self.problem_info[pid]["unsolved_user_sum"] if self.problem_info[pid]["unsolved_user_sum"] > 0 else 0
                        lambda2 = self.problem_info[pid]["solved_attempt_sum"] / self.problem_info[pid]["solved_user_sum"] if self.problem_info[pid]["solved_user_sum"] > 0 else 0
                        if self.problem_history[uid][pid]["isSolved"] == False:
                            if self.problem_history[uid][pid]["attemptCnt"] >= lambda1:
                                data_list.append(1)
                            else:
                                data_list.append(2)
                        else:
                            if self.problem_history[uid][pid]["attemptCnt"] >= lambda2:
                                data_list.append(3)
                            else:
                                data_list.append(4)
                    else:
                        data_list.append(0)
                writer.writerow(data_list)
        
    def append_user_data(self, user_data, temp_up_matrix_fname, problem_info_fname):
        sub_history = sorted(user_data["subs"], key=lambda x : x["submission_time"], reverse=True)

        pid_set = set()

        for sub in sub_history:
            pid_set.add(sub["problem_id"])
        
        problem_history = dict()
        
        for pid in tqdm(pid_set, desc="processing problem record", leave=False):
            for sub in sub_history:
                if sub["problem_id"] == pid:
                    if pid in problem_history:
                        if problem_history[pid]["isSolved"] == True:
                            if sub["verdict_id"] == 90:
                                break
                            else:
                                problem_history[pid]["attemptCnt"] += 1
                    else:
                        if sub["verdict_id"] == 90:
                            problem_history[pid] = {"isSolved": True, "attemptCnt": 1, "solvedTime": sub["submission_time"]}
                        else:
                            problem_history[pid] = {"isSolved": False, "attemptCnt": 1, "solvedTime": sub["submission_time"]}

        with open(problem_info_fname, 'r') as file:
            problem_info = json.load(file)
            problem_info = {int(k): v for k, v in problem_info.items()}
        with open(temp_up_matrix_fname, 'a+', encoding='UTF8', newline='') as file:
            writer = csv.writer(file)
            # write data
            data_list = [user_data["user_id"]]
            for pid in self.pid_list[1:]:
                if pid in problem_history:
                    lambda1 = problem_info[pid]["unsolved_attempt_sum"] / problem_info[pid]["unsolved_user_sum"] if problem_info[pid]["unsolved_user_sum"] > 0 else 0
                    lambda2 = problem_info[pid]["solved_attempt_sum"] / problem_info[pid]["solved_user_sum"] if problem_info[pid]["solved_user_sum"] > 0 else 0
                    if problem_history[pid]["isSolved"] == False:
                        if problem_history[pid]["attemptCnt"] >= lambda1:
                            data_list.append(1)
                        else:
                            data_list.append(2)
                    else:
                        if problem_history[pid]["attemptCnt"] >= lambda2:
                            data_list.append(3)
                        else:
                            data_list.append(4)
                else:
                    data_list.append(0)
            writer.writerow(data_list)

# test
if __name__ == "__main__":
    # bupm = BuildUPMatrix("data/subs_50.json", "data/pid_list.json")
    # bupm.generate_problem_history()
    # bupm.generate_up_matrix()

    bupm = BuildUPMatrix("data/subs_100.json", "data/pid_list.json")
    bupm.generate_problem_history()
    bupm.generate_up_matrix()