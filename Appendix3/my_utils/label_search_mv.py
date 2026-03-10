from pymilvus import MilvusClient, connections
import time
from typing import List, Dict, Any
import threading
import json
import random

# 找到所有父路径
def extract_hierarchical_paths(s, separator='--'):
    # 分割字符串
    parts = s.split(separator)
    # 生成所有父路径
    result = []
    for i in range(len(parts)-1):
        result.append(separator.join(parts[:i+1]))
    # 处理单层情况
    if len(parts) == 1:
        result.append(parts[0])
    return result
# label_list = extract_hierarchical_paths(label)


def label_search(label_list: list = [],
                     milvus_url="http://c-083fddec0b90d74c.milvus.aliyuncs.com:19530",
                     milvus_token="root:GC2023!0814@&^$%#es",
                     db_name="leeman",
                     collection_name="tcm_mix") -> Dict[str, Any]:
    """单个查询函数，通过文本获取向量并进行搜索"""
    thread_name = threading.current_thread().name
    print(f"线程 {thread_name} 开始处理查询: '{label_list}'")

    try:
        # 获取嵌入向量
        start_time = time.time()
        embedding_time = time.time() - start_time

        # 使用线程局部的客户端进行查询
        client = MilvusClient(uri=milvus_url, token=milvus_token, db_name=db_name)
        search_start = time.time()

        # 构建过滤条件
        # query_expr = f'label in {json.dumps(label_list)}'
        query_expr = f'label in {label_list}'
        results = client.query(
            filter=query_expr,
            collection_name=collection_name,
            output_fields=["index", "book", "label", "content"])

        search_time = time.time() - search_start
        total_time = time.time() - start_time

        print(f"线程完成查询: 嵌入时间={embedding_time:.3f}s, 搜索时间={search_time:.3f}s, 总时间={total_time:.3f}s")

        keys = [i['label'] for i in results]
        values = [i['content'] for i in results]
        result = dict(zip(keys, values))
        return result

    except Exception as e:
        print(f"线程 {thread_name} 查询失败: {e}")
        return {
            "query": label_list,
            "error": str(e),
            "results": []
        }


def label_extend(label,
                     milvus_url="http://c-083fddec0b90d74c.milvus.aliyuncs.com:19530",
                     milvus_token="root:GC2023!0814@&^$%#es",
                     db_name="leeman",
                     collection_name="tcm_mix") -> Dict[str, Any]:
    """找到父级和子级"""
    # 父级
    split_label = label.split("--")
    up_label = "--".join(split_label[0:-1])
    # 子级
    try:
        client = MilvusClient(uri=milvus_url, token=milvus_token, db_name=db_name)
        search_start = time.time()

        # 构建过滤条件
        # query_expr = f'label in {json.dumps(label_list)}'
        query_expr = f'label == {json.dumps(label)}'
        results = client.query(
            filter=query_expr,
            collection_name=collection_name,
            output_fields=["index", "book", "label", "content", "next"])
        next_label = eval(results[0]['next'])
        num = min(12, len(next_label))
        next_label = random.sample(next_label, k=num)
    except Exception as e:
        print(f"发生错误，具体原因: {e}")

    label_list = [up_label] + [label] + next_label

    """寻找具体信息"""
    try:
        # 使用线程局部的客户端进行查询
        client = MilvusClient(uri=milvus_url, token=milvus_token, db_name=db_name)

        # 构建过滤条件
        query_expr = f'label in {json.dumps(label_list)}'
        results = client.query(
            filter=query_expr,
            collection_name=collection_name,
            output_fields=["index", "book", "label", "content", "next"])

        sorted_results = sorted(results, key=lambda x: len(x['label']))

    except Exception as e:
        print(f"发生错误，具体原因: {e}")

    """返回节点关系"""
    node_list = []
    relation_list = []
    if up_label != '':
        for index, i in enumerate(sorted_results):
            if index == 0:
                dict_one = {'content':i['content'], 'id':i['label'], 'name':i['label'].split('--')[-1], 'level':'up'}
                node_list.append(dict_one)
            elif index == 1:
                dict_one = {'content':i['content'], 'id':i['label'], 'name':i['label'].split('--')[-1], 'level':'self'}
                node_list.append(dict_one)
                rel_one = {'source':sorted_results[0]['label'], 'target':i['label'], 'value':'link'}
                relation_list.append(rel_one)
            else:
                dict_one = {'content':i['content'], 'id':i['label'], 'name':i['label'].split('--')[-1], 'level':'next'}
                node_list.append(dict_one)
                rel_one = {'source': sorted_results[1]['label'], 'target': i['label'], 'value': 'link'}
                relation_list.append(rel_one)
    else:
        for index, i in enumerate(sorted_results):
            if index == 0:
                dict_one = {'content':i['content'], 'id':i['label'], 'name':i['label'].split('--')[-1], 'level':'self'}
                node_list.append(dict_one)
            else:
                dict_one = {'content':i['content'], 'id':i['label'], 'name':i['label'].split('--')[-1], 'level':'next'}
                node_list.append(dict_one)
                rel_one = {'source': sorted_results[0]['label'], 'target': i['label'], 'value': 'link'}
                relation_list.append(rel_one)

    return node_list, relation_list


if __name__ == "__main__":
    MILVUS_URI = "http://c-083fddec0b90d74c.milvus.aliyuncs.com:19530"
    MILVUS_TOKEN = "root:GC2023!0814@&^$%#es"
    COLLECTION_NAME = "tcm_mix"
    DB_NAME = "leeman"
    label = '中医儿科学'
    # label = '中医儿科学'
    labels = ['诊断学--第四篇 实验诊断--第七章 临床常用生物化学检测--第七节 内分泌激素检测--二、\\xa0临床思维的基本方法--6.伴发疾病诊断', '传染病学--第十章 其他--第六节 感染性发热的诊断思维--【诊断与鉴别诊断】--(二) 细胞外感染--1.感染性心内膜炎（infectiveendocarditis，IE）', '温病学临床运用--上篇 温病学重要原著解释--第一章 温病原著必读--第二节 薛生白《湿热病篇》--三、必读条文释解--（三）邪在气分--【阐释1】--谢昌仁治案--主诉：', '住院医师规范化培训急诊科示范案例_陆一鸣--案例2 急性发热--四、要点与讨论--4. 鉴别诊断', '中西医结合内科学--第二章 循环系统疾病--第八节 感染性心内膜炎--【临床表现】--一、主要症状', '外科学--第九章 围术期处理--第三节 术后并发症的防治--（二）术后发热与低体温--1.发热', '住院医师规范化培训_儿科示范案例_黄国英--案例8 惊厥--三、病例分析--1.病史特点', '中国当代针灸名家医案--蔺云柱医案--医案选辑--例3 肌衄 （血小板减少性紫癫）--检查', '医圣张仲景奇方妙治_王竹星--辨可下病脉证并治方--方十九--【白话解】', '温病学临床精要--第三篇 温病基本方剂运用体会--第九章 达 原 饮《温疫论》--5.临床运用--(3)谢昌仁治邪伏膜原案--主诉：', '针灸疑难奇症医案荟萃_张登部.md--二、外科疾病--丹 毒--检查：', '中医外科学--第六章 疮疡--第四节 发--二、臀痛']
    # labels = ['针灸名家医案精选导读_赵建新.md--第1章 内科病证--第三十二节面 肌 𥆧 动']
    # 寻找节点具体信息
    # for i in labels:
    #     print(i)
    #     results = label_search([i],
    #                      milvus_url=MILVUS_URI,
    #                      milvus_token=MILVUS_TOKEN,
    #                      db_name=DB_NAME,
    #                      collection_name=COLLECTION_NAME)
    results = label_search(labels,
                           milvus_url=MILVUS_URI,
                           milvus_token=MILVUS_TOKEN,
                           db_name=DB_NAME,
                           collection_name=COLLECTION_NAME)

    # 扩展上下级节点
    node_list, relation_list = label_extend(label,
                     milvus_url=MILVUS_URI,
                     milvus_token=MILVUS_TOKEN,
                     db_name=DB_NAME,
                     collection_name=COLLECTION_NAME)


    print(1)