import json
import pandas as pd

filename = input('Result filename: ')
out_filename = input('Output filename: ')

roll_list = pd.read_csv('data.csv').values.tolist()
roll_map = {}
for stud in roll_list:
    roll_map[stud[1]] = stud[0]

# result_data = []
with open(filename) as f:
    result_data = json.loads(f.read())

out = []
for stud in result_data:
    roll = list(stud.keys())[0]
    name = roll_map[roll]
    f_res = [roll, name]
    if(stud[roll][0][0] == "NA"):
        f_res.extend(["NOT AVAILABLE"])
    else :
        stud_result = json.loads(stud[roll])
        res_out = []
        for subject in stud_result:
            res_out.append(list(subject.values()))
        res_out = [j for i in res_out for j in i]
        f_res.extend(res_out)
    out.append(f_res)

df = pd.DataFrame(out)
df.to_csv(open(out_filename,'w'))