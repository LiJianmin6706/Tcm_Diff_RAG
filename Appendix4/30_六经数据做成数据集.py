import os
import pandas as pd
from tqdm import tqdm
import json

path = 'Jingfang_train.xlsx'
df = pd.read_excel(path)


train_list = []
for index, row_data in df.iterrows():
    chief_complaint = row_data['chief_complaint']
    description = row_data['systom']
    # detection = row_data['detection']
    answer = row_data['answer']
    template = f''' 
    主诉：{chief_complaint}
    症状及查体：{description}
    你针对以上病历，以六经辨证的思维，判断患者属于什么六经证候，并给出详细的分析
    '''
    if pd.isna(row_data['answer']):
        pass
    else:
        case = {"instruction":'你是一名中医六经辩证专家，善于对病历进行证候诊断，你需要对病历进行分析，并生成有关联关系的三元组列表', "input": template, "output":answer}
    train_list.append(case)

save_path = 'liujing_qa.json'
with open(save_path, 'w', encoding='UTF-8') as f:
    json.dump(train_list, f, ensure_ascii=False, indent=2)

print(1)