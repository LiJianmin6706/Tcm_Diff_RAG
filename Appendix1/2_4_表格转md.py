import pandas as pd
from tqdm import tqdm
import requests
import json
import os
from my_utils.utils import adjust_list_length
import functools
# os.environ.pop("http_proxy", None)
# os.environ.pop("https_proxy", None)

path = 'data/xlsx_raw'
xlsx_path = [os.path.join(path,j) for j in os.listdir(path)]
books = [i.split('.xlsx')[0].split('\\')[1] for i in xlsx_path]

'''
设定参数
'''
for book_num, book_name in enumerate(books):
    print(book_num, book_name)
    df_path = xlsx_path[book_num]
    # df_path = f'convert/xlsx_files/{book_name}.xlsx' # 选择处理的文件
    df_title_path = f'data/save/{book_name}_title.xlsx' # 保存层级文件路径
    df = pd.read_excel(df_path)
    md_path = f'data/md/{book_name}.md'
    # url = 'http://10.0.9.54:5003/chat'
    url = 'http://10.0.11.94:5004/chat'
    title_num = 10 # 每次转换的标题个数
    max_attempts = 10

    file_name = list(df["book"])[0]
    save_path = f'{md_path}/{file_name}.md'

    df_title = df.loc[(df['label'] == 'Title') | (df['label'] == 'Subtitle')]
    df_title_list = list(df_title['text'])

    # 按title_num个元素切分
    df_title_list_split_all = []
    for i in range(0, len(df_title_list), title_num):
        df_title_list_split_all.append(df_title_list[i:i + title_num])

    '''
    产出标题层级
    '''
    old_title_list, old_level_list, df_depth_list = [], [], []
    for index, df_title_list_split in enumerate(tqdm(df_title_list_split_all, total=len(df_title_list_split_all))):
        if index == 0:
            old_title = []
            old_level = []
            user_input = f'''
                请参考例子，根据标题列表，输出标题对应的层级列表。请务必保证以下两点：
                1.输出的标题层级是列表；
                2.输出的层级列表的元素与标题列表的元素与个数保持一致；
                以下是第一个例子
                这是标题列表：['第 一篇 临床实验室与检验医师', '第一章 临床实验室与质量管理', '第一节 临床实验室', '1）生理性变异：', '2）生活习惯：']
                这是输出的层级列表：[2, 3, 4, 5, 5]
                这是你要处理的标题列表：{df_title_list_split}
                请参考例子，输出本轮标题对应的层级列表：
            '''
            data = json.dumps({"input": user_input})

            # 加入容错重试机制
            try:
                response = requests.post(url, json={"input": user_input})
                output_levle = eval(response.json()['reply'])
                assert len(output_levle) == len(df_title_list_split)
                # break  # 如果函数执行成功，退出循环
            except Exception as e:
                print('输出失败')
                expect_output_levle = len(df_title_list_split)
                output_levle = adjust_list_length(output_levle, expect_output_levle)


            old_title_list.append(df_title_list_split)
            old_level_list.append(output_levle)
            df_depth_list.extend(output_levle)
        else:
            old_title = old_title_list[-1]
            old_level = old_level_list[-1]
            start_title = df_title_list[0:20]
            start_level = df_depth_list[0:20]
            user_input = f'''
            请参考例子，根据标题列表，输出标题对应的层级列表。请务必保证以下两点：
            1.输出的标题层级是列表；
            2.输出的层级列表的元素与标题列表的元素与个数保持一致；
            3.本轮标题的层级要承接上一轮标题的层级
            4.本轮标题的层级总体要参考初始层级，如‘第一章’和‘第二章’的层级一致，‘第一节’和‘第二节’的层级一致
            这是初始的标题列表:{start_title}
            这是初始的标题的层级列表:{start_level}
            这是上一轮的标题列表：{old_title}
            这是上一轮标题的层级列表：{old_level}
            这是你要处理的本轮标题列表：{df_title_list_split}
            请参考初始的标题层级，并根据上一轮的关系输出本轮标题对应的层级列表：
            '''
            data = json.dumps({"input": user_input})

            # 加入容错重试机制
            try:
                response = requests.post(url, json={"input": user_input})
                output_levle = eval(response.json()['reply'])
                assert len(output_levle) == len(df_title_list_split)
                # break  # 如果函数执行成功，退出循环
            except Exception as e:
                print('输出失败')
                expect_output_levle = len(df_title_list_split)
                output_levle = adjust_list_length(output_levle, expect_output_levle)

            old_title_list.append(df_title_list_split)
            old_level_list.append(output_levle)
            df_depth_list.extend(output_levle)


    '''
    增加标题层级一列到dataframe
    '''
    df_title['depth'] = df_depth_list

    change_index_list = list(df_title.index)
    df['depth'] = int(100)  # 首先设置深度都是100，然后特殊的再个别去改
    for row_index, row_data in df.iterrows():
        if row_index in change_index_list:
            df.loc[row_index, 'text'] = df_title.loc[row_index, 'text']
            num = df_title.loc[row_index, 'depth']
            # print(num)
            if type(num)==list:
                num = num[0]
            df.loc[row_index, 'depth'] = int(num)
        else:
            pass

    df = df.reset_index(drop=True)  # 不重置索引后面会报错
    df = df.dropna(subset=['text'])
    df.to_excel(df_title_path, index=False)

    '''
    写入md
    '''
    with open(md_path, 'a', encoding='utf-8') as f:
        f.write('# {0}'.format(file_name) + '\n')
    for row_index, row_data in df.iterrows():
        layer = row_data['depth']
        if layer <= 10:
            layer_str = '#' * layer
            with open(md_path, 'a', encoding='utf-8') as f:
                f.write(layer_str + ' ' + str(row_data['text']) + '\n')
        else:
            with open(md_path, 'a', encoding='utf-8') as f:
                # f.write(row_data['text'] + '\n') # 写下英文
                f.write(str(row_data['text']) + '\n')



