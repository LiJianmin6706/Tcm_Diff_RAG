from my_utils.vector_search import MyEmbeddings, ES_search
from elasticsearch import Elasticsearch
from elasticsearch import AsyncElasticsearch
import asyncio
import time
import warnings


warnings.filterwarnings('ignore')



def tuple_search_fun(query_list, books, es, INDEX_NAME, emb_model, emb_api_base, emb_key, k_num):
    '''
    :param query_list: 查询的三元组列表
    :param es: es检索示例
    :param INDEX_NAME: es的索引名称
    :param emb_model: 嵌入模型名称
    :param emb_api_base: 调用的url
    :param emb_key: 模型的key
    :param k_num: 一个输入的三元组匹配多少条对应的三元组
    :return:
    '''
    es_instances = ES_search(es, INDEX_NAME, emb_model, emb_api_base, emb_key)

    async def get_tuple():
        tasks = []
        for query in query_list:
            task = asyncio.create_task(es_instances.async_match_tuple(query, books, k_num))
            tasks.append(task)
        results = await asyncio.gather(*tasks)

        return results

    results = asyncio.run(get_tuple())

    label_list = []
    tuple_list = []
    for index, result in enumerate(results):
        tuple = [i[0].page_content for i in result]
        tuple_list.extend(tuple)
        labels = [i[0].metadata['label'] for i in result]
        label_list.extend(labels)

    output = list(zip(tuple_list, label_list))
    unique_output = []
    for t in output:
        if t not in unique_output:
            unique_output.append(t)

    return unique_output


if __name__ == "__main__":
    emb_model = "text-embedding-v3"
    emb_api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    emb_key = 'sk-e5ed91a78f424009821dade731c0dffb'
    # es = Elasticsearch(["https://10.6.82.132:9200"],
    #                    basic_auth=('elastic', 'GDIP@ssw0rd'), verify_certs=False, ca_certs=False)
    es = Elasticsearch(["http://es-cn-9lb3cjnbp000m6xzo.public.elasticsearch.aliyuncs.com:9200"],
                       http_auth=('elastic', 'GC2023!0814@&^$%#es'), timeout=100)

    INDEX_NAME = 'tcm_spo_v1'
    books = ['中医学', '方剂学', '标准方剂']

    k_num = 2

    query_list = [('反复咳嗽、发热1年', '治疗药物', '')]
    query_list = [('反复咳嗽、发热1年', '可能属于', '慢性肺部疾病或体虚外感'),
                   ('不怕风冷，汗不多，紧运动出汗', '反映', '体表阳气不足，汗孔开合失常'),
                   ('汗后吹风易感冒，汗后凉', '表明', '体质偏虚，易感外邪'), ('手脚自觉偏凉', '属于', '阳虚表现'),
                   ('无口干口苦，无心慌胸闷，无头晕耳鸣头痛，无四肢酸疼', '排除', '内热、心血管及风湿类疾病'),
                   ('上周痰黄，现偶尔有痰，偏白，痰易咳', '表明', '痰湿内停，逐渐转化'),
                   ('不发烧时四肢皮肤痒，发烧时不痒', '可能与', '体内湿热或血热有关'),
                   ('皮肤偏干，痒时皮肤无红色丘疹', '反映', '血虚风燥或皮肤失养'),
                   ('既往喜冷饮，现喜饮热', '反映', '体质或病情变化，由热转寒'),
                   ('睡觉一定要盖肚子', '表明', '腹部易受凉，脾胃虚寒'), ('大便每日2-3次，不干不稀', '属于', '大便正常'),
                   ('小便可，无灼热', '排除', '尿道感染或内热'), ('脉浮弦数', '反映', '外感风寒或肝郁气滞，兼有热象'),
                   ('舌淡紫红嫩，苔黄白腻边齿痕', '表明', '气血两虚，湿热内蕴'),
                   ('下睑红鲜', '可能与', '阴虚火旺或血热有关'), ('面部火痤', '属于', '血热或湿热上蒸'),
                   ('腹薄拘', '反映', '腹部肌肉紧张，可能有腹痛或肝郁'), ('下肢甲错，抓痕', '表明', '血虚风燥，肌肤失养'),
                   ('手微潮微凉', '属于', '阳虚湿困表现')]





    start_time = time.time()
    output = tuple_search_fun(query_list, books, es, INDEX_NAME, emb_model, emb_api_base, emb_key, k_num)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"程序运行时间：{elapsed_time}秒")

    labels_all = []
    for i in output:
        label_list = i[1]
        labels_all.extend(label_list)





    print('完成')