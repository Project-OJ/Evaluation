import pandas as pd
import os
import random
import math
import json
import time
from tqdm import tqdm

MONTH = 2629743

class CollaborativeFilter:
    def __init__(self, ui_matrix_filename, problem_history_filename, p_info_fname, user_id=0):
        self.ui_matrix_filename = ui_matrix_filename
        self.problem_history_filename = problem_history_filename
        self.user_id = user_id
        self.dataset = None
        self.problem_history = None
        self.uid_list = list()
        self.decay_period = MONTH * 1
        self.smc_similar_val = 0.5
        self.useDecay = True
        with open("data/pid_list.json", 'r') as file:
            self.pid_list = json.load(file)
        with open(p_info_fname, 'r') as file:
            self.problem_info = json.load(file)
            self.problem_info = {int(k): v for k, v in self.problem_info.items()}
    
    def initialize(self):
        if not os.path.isfile(self.ui_matrix_filename):
            self.quit("Input file doesn't exist or it's not a file: {0}".format(self.ui_matrix_filename))
        
        if not os.path.isfile(self.problem_history_filename):
            self.quit("Input file doesn't exist or it's not a file: {0}".format(self.problem_history_filename))

        # os.system("cls")
        self.load_ui_matrix(self.ui_matrix_filename)
        self.load_problem_history(self.problem_history_filename)
        
    def isUidInData(self, uid):
        users = self.dataset.keys()
        return uid in users
        
    def smc_similarity(self, user1, user2):
        result = 0.0
        if user1 in self.dataset.keys() and user2 in self.dataset.keys():
            user1_data = self.dataset[user1]
            user2_data = self.dataset[user2]
        else:
            return 0

        matching_coef_cnt = 0.0
        total_coef_cnt = 0.0

        for pid in self.pid_list:
            if user1_data[pid] != 0 or user2_data[pid] != 0:
                if user1_data[pid] == user2_data[pid]:
                    matching_coef_cnt += 1
                elif user1_data[pid] <= 2 and user2_data[pid] <= 2 and user1_data[pid] != 0 and user2_data[pid] != 0:
                    matching_coef_cnt += self.smc_similar_val
                elif user1_data[pid] > 2 and user2_data[pid] > 2:
                    matching_coef_cnt += self.smc_similar_val
                total_coef_cnt += 1
        
        if total_coef_cnt > 0:
            result = matching_coef_cnt / total_coef_cnt
        else:
            result = 0
        return result

    def common_pid(self, user1_data, user2_data):
        result = []
        for pid in self.pid_list:
            if user1_data[pid] == user2_data[pid]:
                result.append(pid)
        return result

    def k_nearest_neighbors(self, user, k):
        neighbors = []

        for uid in tqdm(self.dataset, desc="knn"):
            if uid == user:
                continue
            similarity = self.smc_similarity(user, uid)
            neighbors.append([uid, similarity])
        sorted_neighbors = sorted(neighbors, key= lambda neighbor: neighbor[1], reverse=True)
        
        return sorted_neighbors[:k]
    
    def decay_function(self, date):
        time_passed = time.time() - date
        return math.exp(-1 * time_passed / self.decay_period)

    def get_unsolved_pid(self, user, k_nearest_neighbors):
        result = set()
        for neighbor in tqdm(k_nearest_neighbors, desc="getting unsolved problems"):
            for pid in self.pid_list:
                neighbor_id = neighbor[0]
                if self.dataset[user][pid] == 0 and self.dataset[neighbor_id][pid] != 0:
                    result.add(pid)
        return result
        
    def generate_recommendation(self, user_id, k_nearest_neighbors, rec_num):
        result = []
        pid_list = self.get_unsolved_pid(user_id, k_nearest_neighbors)
        # check if nearest_neighbors are in data base
        
        for pid in pid_list:
            score = 0.0
            for neighbor in k_nearest_neighbors:
                neighbor_id = neighbor[0]
                neighbor_similarity = neighbor[1]
                rating = self.dataset[neighbor_id][pid]
                if str(neighbor_id) in self.problem_history:
                    if self.useDecay == True and str(pid) in self.problem_history[str(neighbor_id)]:
                        date = self.problem_history[str(neighbor_id)][str(pid)]["solvedTime"]
                        score += neighbor_similarity * rating * self.decay_function(date)
                    else:
                        score += neighbor_similarity * rating
            result.append((pid, score))
        
        result = sorted(result, key=lambda x: (-x[1], x[0]))

        if len(result) > rec_num:
            return result[:rec_num]
        else:
            print("The recommendations available is less than the requested amount")
            return result[:]

    def load_ui_matrix(self, ui_matrix_filename):
        print("reading " + ui_matrix_filename + "...")
        data_frame = pd.read_csv(ui_matrix_filename, header=0, index_col=0).T
        print("transforming matrix to dictionary...")
        self.dataset = data_frame.to_dict()
        self.uid_list = data_frame.columns
        for uid in tqdm(self.dataset, desc="processing data"):
            self.dataset[uid] = {int(k): v for k, v in self.dataset[uid].items()}
    
    def append_user_data(self, uid, user_ph):
        data_list = {}
        for pid in self.pid_list:
            if pid in user_ph:
                lambda1 = self.problem_info[pid]["unsolved_attempt_sum"] / self.problem_info[pid]["unsolved_user_sum"] if self.problem_info[pid]["unsolved_user_sum"] > 0 else 0
                lambda2 = self.problem_info[pid]["solved_attempt_sum"] / self.problem_info[pid]["solved_user_sum"] if self.problem_info[pid]["solved_user_sum"] > 0 else 0
                if user_ph[pid]["AC"] == False:
                    if user_ph[pid]["attempt_cnt"] >= lambda1:
                        data_list[pid] = 1
                    else:
                        data_list[pid] = 2
                else:
                    if user_ph[pid]["attempt_cnt"] >= lambda2:
                        data_list[pid] = 3
                    else:
                        data_list[pid] = 4
            else:
                data_list[pid] = 0
        self.dataset[uid] = data_list
    
    def load_problem_history(self, problem_history_filename):
        print("reading " + problem_history_filename + "...")
        with open(problem_history_filename, 'r', encoding="utf-8") as file:
            self.problem_history = json.load(file)

    def get_random_uid(self):
        return random.choice(self.uid_list)

    def display(self, recommendation):
        print("pid\t score")
        for problem in recommendation:
            print(problem[0], "\t", problem[1])

    def quit(self, err_desc):
        raise SystemExit('\n' + "PROGRAM EXIT: " + err_desc + '\n')
    
    def getRecom(self, sim_ph):
        uid = 0
        k = 120
        recom_num = 5
        self.append_user_data(uid, sim_ph)
        knn = self.k_nearest_neighbors(uid, k)
        result = self.generate_recommendation(uid, knn, recom_num)
        recom_list = {pid for pid, score in result}
        return recom_list

# recommender system test
if __name__ == "__main__":
    ui_matrix_filename = "CFRS_data/up_matrix_50.csv"
    problem_history_filename = "CFRS_data/p_history_50.json"
    p_info_fname = "CFRS_data/p_info_50.json"

    cf = CollaborativeFilter(ui_matrix_filename, problem_history_filename, p_info_fname)
    cf.initialize()

    while True:
        os.system("cls")
        k = int(input("Please enter the number of nearest-neighbor: "))
        recommend_num = int(input("Please enter the desired amount of recommendation: "))

        while True:
            input_uid = int(input("Please enter a uid, or 0 to pick a random uid: "))
            if input_uid != 0:
                if cf.isUidInData(input_uid) == True:
                    cf.user_id = input_uid
                    user_id = input_uid
                    break
                else:
                    print("Error: user id not in database")
            else:
                user_id = cf.get_random_uid()
                break

        while True:
            input_useDecay = input("Use decay? (y/n): ")
            if input_useDecay.lower() == "y":
                cf.useDecay = True
                break
            elif input_useDecay.lower() == "n":
                cf.useDecay = False
                break
            else:
                print("invalid input")

        k_nearest_neighbors = cf.k_nearest_neighbors(user_id, k)
        recommendation = cf.generate_recommendation(user_id, k_nearest_neighbors, recommend_num)

        print("Target uid:", user_id)
        cf.display(recommendation)

        while True:
            input_str = input("Continue (c) / Quit (q): ")
            if input_str.lower() == 'c':
                break
            elif input_str.lower() == 'q':
                raise SystemExit()
            else:
                print("invalid input")