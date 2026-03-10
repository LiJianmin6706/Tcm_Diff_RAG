# -*- coding: utf-8 -*-
from my_utils.tuple_generate import tuple_generation_fun
from my_utils.tuple_search_mv import concurrent_search, get_labels
from my_utils.content_search_mv import concurrent_search_content
from my_utils.label_search_mv import label_search
from my_utils.llm_filter import filter_1, summary
from my_utils.plot import plot
from openai import OpenAI
import random
import time
import re

api_base = "http://47.99.155.171:3000/v1"
api_key = ''
spo_model = "空"
filter_model = '空'

emb_model = "text-embedding-v3"
emb_api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
emb_key = ''
emb_client = OpenAI(
    api_key=emb_key,
    base_url=emb_api_base,
)

# milvus配置
MILVUS_URI = ""
MILVUS_TOKEN = "root:GC2023!0814@&^$%#es"
COLLECTION_NAME_1 = "spo_v2"
COLLECTION_NAME_2 = "tcm_mix"
DB_NAME = "leeman"
book_list = []   # 替换成你的书列表
spo_num = 10
content_num = 1

input_text = '''
主诉：头晕伴手麻2月
现病史：
患者2月前开始出现头晕伴手麻，未予重视，昨日出现头晕加重，无心慌胸闷，无汗出乏力，无晕厥黑矇，至社区医院测血压，收缩压210mmHg，急至我院门诊就诊，测血压180/90mmHg，予代文80mg qd、拜新同1粒 qd，建议其住院治疗，今日拟“高血压急症”收住入院。入院时：患者头晕头昏，无头痛，时欲太息，遇烦劳、郁怒而加重，容易加重，嗳气则舒，无心慌胸闷，纳可，二便尚调，夜寐一般。
'''

if spo_num==0:
    search_tuple = []
    generate_tuple = [input_text]
elif spo_model=="空":
    '''
    2.检索三元组
    '''
    generate_tuple = [input_text]
    start_time = time.time()
    search_tuple = concurrent_search(emb_client, model_name=emb_model, queries=generate_tuple, book_list=book_list, top_k=spo_num,
                                max_workers=len(generate_tuple),
                                milvus_url=MILVUS_URI,
                                milvus_token=MILVUS_TOKEN,
                                db_name=DB_NAME,
                                collection_name=COLLECTION_NAME_1)
    end_time = time.time()
    elapsed_time = end_time - start_time
    # 并发处理后，顺序会乱，对生成的三元组进行排序
    index_map = {item: idx for idx, item in enumerate(generate_tuple)}
    search_tuple = sorted(search_tuple, key=lambda x: index_map[x['query']])

    print(f"搜索三元组时间：{elapsed_time}秒")

else:
    '''
    1.生成三元组
    '''
    start_time = time.time()
    # tuple_base = 'http://10.0.9.54:9000/v1'
    # tuple_key = 'EMPTY'
    # tuple_model = 'Qwen2.5-7B'
    # generate_tuple = tuple_generation_fun(input_text, tuple_model, tuple_base, tuple_key)
    generate_tuple = tuple_generation_fun(input_text, spo_model, api_base, api_key)
    generate_tuple.append(input_text)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"生成三元组时间：{elapsed_time}秒")


    '''
    2.检索三元组
    '''
    start_time = time.time()
    search_tuple = concurrent_search(emb_client, model_name=emb_model, queries=generate_tuple, book_list=book_list, top_k=spo_num,
                                max_workers=len(generate_tuple),
                                milvus_url=MILVUS_URI,
                                milvus_token=MILVUS_TOKEN,
                                db_name=DB_NAME,
                                collection_name=COLLECTION_NAME_1)
    end_time = time.time()
    elapsed_time = end_time - start_time
    # 并发处理后，顺序会乱，对生成的三元组进行排序
    index_map = {item: idx for idx, item in enumerate(generate_tuple)}
    search_tuple = sorted(search_tuple, key=lambda x: index_map[x['query']])

    print(f"搜索三元组时间：{elapsed_time}秒")

'''
3.输入文本检索tim_mix
'''
start_time = time.time()
# input_query = [input_text] + generate_tuple
search_content = concurrent_search_content(emb_client, model_name=emb_model, queries=[input_text], book_list=book_list, top_k=content_num,
                                    max_workers=len(generate_tuple),
                                    milvus_url="http://c-083fddec0b90d74c.milvus.aliyuncs.com:19530",
                                    milvus_token="root:GC2023!0814@&^$%#es",
                                    db_name="leeman",
                                    collection_name=COLLECTION_NAME_2)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"搜索条文时间：{elapsed_time}秒")

'''
4.获取条文
'''
label_list_1 = get_labels(search_tuple)
label_list_2 = get_labels(search_content)
label_list = label_list_1 + label_list_2
label_unique = list(dict.fromkeys(label_list))
content_dict = label_search(label_unique,
                       milvus_url=MILVUS_URI,
                       milvus_token=MILVUS_TOKEN,
                       db_name=DB_NAME,
                       collection_name=COLLECTION_NAME_2)

'''
5.得到召回内容
'''
# recall_dic是label对应的内容和三元组
recall_dict = {}
select_spos = []
for i in search_tuple:
    text_1 = i['query']
    content = ''
    for j in i['results']:
        search = j['entity']['tuple']
        text_2 = search
        select_spos.append(text_2)
        for k in eval(str(j['entity']['label'])):
            source = k
            if source in content_dict.keys():
                content = content_dict[source]

                if source not in recall_dict.keys():
                    recall_dict[source] = f'内容：{content}\n@@@@\n问题相关的三元组：{text_1}\n匹配的三元组：{text_2}\n'
                else:
                    recall_dict[source] += f'问题相关的三元组：{text_1}\n匹配的三元组：{text_2}\n'

for i in content_dict.keys():
    if i not in recall_dict.keys():
        recall_dict[i] = f'内容：{content_dict[i]}\n@@@@'


recall_list = []
for key, value in recall_dict.items():
    spo = value.split('@@@@')[1]
    label = key
    content = value.split('@@@@')[0]
    recall_one = f'{spo}\n来源：{label}\n\n{content}'
    recall_list.append(recall_one)

'''
6.二次筛选
'''
if filter_model == "空":
    print('不执行筛选')
    recall_list_filter = recall_list
    recall_list_filter_plot = recall_list_filter
    filter_docs = recall_list
    summary_docs = recall_list

else:
    print(f'执行总结')
    filter_index, filter_docs, summary_docs = summary(filter_model, input_text, recall_list)
    recall_list_filter = summary_docs
    recall_list_filter_plot = [recall_list[i] for i in filter_index]


out_dict_list = []
label_all = []
for index, (content, summary_text) in enumerate(zip(filter_docs, summary_docs)):
    label = content.split('来源：')[1].split('\n')[0]
    label_all.append(label)
    out_dict = {"index": index + 1, "summary": summary_text, "source": label, "content": content.split('内容：')[1] }
    out_dict_list.append(out_dict)
'''
7.构建节点
'''
node_list = [{"id":"问题", "name":"问题", "content":input_text}]
relation_list = []

for recall in recall_list_filter_plot:
    pattern_1 = re.compile('问题相关的三元组：(.*?)\n', re.I)
    pattern_2 = re.compile('匹配的三元组：(.*?)\n', re.I)
    pattern_3 = re.compile('来源：(.*?)\n', re.I)
    gen_spos = re.findall(pattern_1, recall)
    match_spos = set(re.findall(pattern_2, recall))
    title = re.findall(pattern_3, recall)[0]

    # 实体节点
    if match_spos == set():
        book_node = {"id": title, "name": title.split('--')[-1], "content": content_dict[title]}
        rel = {"source": "问题", "target": title, 'value': 'link'}
        if book_node not in node_list:
            node_list.append(book_node)
        if rel not in relation_list:
            relation_list.append(rel)
    else:
        for i in match_spos:
            spo = eval(i)
            subject_id = str([0]) + '_entity'
            object_id = str(spo[2]) + '_entity'
            subject_dict = {"id": subject_id, "name": spo[0], "content": ""}
            object_dict = {"id": object_id, "name": spo[2], "content": ""}
            rel_1 = {"source": subject_id, "target": object_id, 'value': spo[1]}
            rel_2 = {"source": "问题", "target": subject_id, 'value': 'link'}
            if subject_dict not in node_list:
                node_list.append(subject_dict)
            if object_dict not in node_list:
                node_list.append(object_dict)
            if rel_1 not in relation_list:
                relation_list.append(rel_1)
            if rel_2 not in relation_list:
                relation_list.append(rel_2)
            if title in content_dict.keys():
                book_node = {"id": title, "name": title.split('--')[-1], "content": content_dict[title]}
            rel_3 = {"source": object_id, "target": title, 'value': 'link'}
            if book_node not in node_list:
                node_list.append(book_node)
            if rel_3 not in relation_list:
                relation_list.append(rel_3)


'''
6.作图
'''
pic_path = '图.html'
graph = plot(node_list, relation_list, pic_path)
graph.render(pic_path)

print('完成')