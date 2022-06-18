import json

from numpy import mat

DIF_TH1 = 3
DIF_TH2 = 5
EASY_SCORE = 1
APPRO_SCORE = 5
HARD_SCORE = 3

def keystoint(x):
    return {int(k): v for k, v in x.items()}

class RSEvaluator:
    def __init__(self, p_history_fname, rs, ppr=10, sim_init_length=10):
        self.rs = rs    # recommender system instance
        self.ppr = ppr  # problem per round
        self.sim_init_length = sim_init_length   # the initial length of simulated problem history
        with open(p_history_fname, 'r') as file:
            self.user_dict = json.load(file)

    def simulate(self, onlyAC=False):
        mpr_log = dict()
        for uid, ph in self.user_dict.items():
            sim_ph = dict(list(ph.items())[:self.sim_init_length])
            index = self.sim_init_length
            round_cnt = 0
            while True:
                round_cnt += 1
                actual_p = dict(list(ph.items())[index:index + self.ppr])
                actual_p = keystoint(actual_p)
                rankList = self.rs.getRankList(sim_ph)

                # print("recommended:", recom_p)
                print("actual:", list(actual_p.keys()))

                mpr = self.evalRecom(rankList, actual_p, onlyAC)

                index += self.ppr
                sim_ph.update(actual_p)
                self.recordScore(mpr_log, uid, mpr)

                if index >= len(ph):
                    break
        return mpr_log

    def evalRecom(self, rank_list, actual_p, p_history, onlyAC=False):
        # using mean percentile ranking
        mpr = 0.0
        for pid in actual_p:
            if onlyAC is True and p_history[str(pid)]["AC"] == False:
                break
            # percentage of the ranking (0% - 100%)
            try:
                mpr += rank_list.index(pid) / (len(rank_list) - 1)
            except ValueError as error:
                print(error)
                mpr += 1
        # get rank percentage average
        mpr /= len(actual_p)
        return mpr

    def recordScore(self, mpr_log, uid, mpr,):
        if uid not in mpr_log:
            mpr_log[uid] = list()
        mpr_log[uid].append(mpr)