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

    def simulate(self):
        score_log = dict()
        for uid, ph in self.user_dict.items():
            score = 0   # The score RS earned from this user
            tp = 0      # True positive (AC'ed and recommended)
            fp = 0      # False positive (recommended but didn't AC)
            sim_ph = dict(list(ph.items())[:self.sim_init_length])
            index = self.sim_init_length
            round_cnt = 0
            while index < len(ph):
                round_cnt += 1
                actual_p = dict(list(ph.items())[index:index + self.ppr])
                actual_p = keystoint(actual_p)
                recom_p = self.rs.getRecom(sim_ph)

                # print("recommended:", recom_p)
                # print("actual:", list(actual_p.keys()))

                self.evalRecom(recom_p, actual_p, ph, score, tp, fp)
                index += self.ppr
                sim_ph.update(actual_p)
            self.recordScore(score_log, uid, score, tp, fp)
        return score_log

    def evalRecom(self, recom_p, actual_p, p_history, score, tp, fp):
        for pid in recom_p:
            if pid in actual_p and p_history[str(pid)]["AC"] == True:
                tp += 1
                # If problem is easy for user
                if p_history[str(pid)]["attempt_cnt"] < DIF_TH1:
                    score += EASY_SCORE
                # If problem is appropreate for user
                elif p_history[str(pid)]["attempt_cnt"] < DIF_TH2:
                    score += APPRO_SCORE
                # If problem is hard for user
                else:
                    score += HARD_SCORE
            elif pid in actual_p and p_history[str(pid)]["AC"] == False:
                fp += 1

    def recordScore(self, score_log, uid, score, tp, fp):
        score_log[uid] = {
            "score": score,
            "tp": tp,
            "fp": fp
        }