import pandas as pd

file = 'data/save/data.jsonl'
# 读取JSONL文件
df = pd.read_json(file, lines=True, encoding='utf-8')



# 创建一个空列表，用于存储切割后的小DataFrame
split_dfs = []

# 使用groupby方法将数据按照每10行分组
groups = df.groupby(df.book)

# 遍历分组，并将每个分组的数据存储到split_dfs列表中
for file, group in groups:
    save_path = f'data/xlsx_raw/{file}.xlsx'
    group.to_excel(save_path, index=False)


print(1)