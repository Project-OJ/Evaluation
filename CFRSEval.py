from CollabFilter import CollaborativeFilter
from RSEvaluator import RSEvaluator
import sys
import json

arg = sys.argv[1]

up_matrix_50_fname = "CFRS_data/up_matrix_50.csv"
up_matrix_100_fname = "CFRS_data/up_matrix_100.csv"
ph_50_fname = "CFRS_data/p_history_50.json"
ph_100_fname = "CFRS_data/p_history_100.json"
p_info_50_fname = "CFRS_data/p_info_50.json"
p_info_100_fname = "CFRS_data/p_info_100.json"

if arg == "50":
    cf = CollaborativeFilter(up_matrix_50_fname, ph_50_fname, p_info_50_fname)
    cf.initialize()
    rse = RSEvaluator("data/50_phistory.json", cf, 10, 10)
    result = rse.simulate()
    print(json.dumps(result, indent=2))
elif arg == "100":
    cf = CollaborativeFilter(up_matrix_100_fname, ph_100_fname, p_info_100_fname)
    cf.initialize()
    rse = RSEvaluator("data/100_phistory.json", cf, 10, 10)
    result = rse.simulate()
    print(json.dumps(result, indent=2))
else:
    print("Invalid argument.")

with open("test_result_50.json", 'w') as file:
    json.dump(result, file, indent=2)