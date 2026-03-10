from pymilvus import MilvusClient, connections
from openai import OpenAI
import concurrent.futures
import time
from typing import List, Dict, Any
import threading
import json
import google


def get_embedding(emb_client, text: str, model_name: str) -> List[float]:
    """获取文本的向量表示"""
    try:
        response = emb_client.embeddings.create(
            model=model_name,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"获取嵌入向量失败: {e}")
        raise

def search_by_vector(emb_client, model_name, query: str, book_list: list = [], top_k: int = 3,
                     milvus_url="http://c-083fddec0b90d74c.milvus.aliyuncs.com:19530",
                     milvus_token="root:GC2023!0814@&^$%#es",
                     db_name="leeman",
                     collection_name="spo") -> Dict[str, Any]:
    """单个查询函数，通过文本获取向量并进行搜索"""
    thread_name = threading.current_thread().name
    print(f"线程 {thread_name} 开始处理查询: '{query}'")

    try:
        # 获取嵌入向量
        start_time = time.time()
        vector = get_embedding(emb_client, query, model_name)
        embedding_time = time.time() - start_time

        # 使用线程局部的客户端进行查询
        thread_local = threading.local()
        def get_milvus_client():
            """获取线程局部的Milvus客户端，确保线程安全"""
            if not hasattr(thread_local, "client"):
                print(f"为线程 {threading.current_thread().name} 创建新的Milvus客户端")
                thread_local.client = MilvusClient(uri=milvus_url, token=milvus_token, db_name=db_name)
            return thread_local.client

        client = get_milvus_client()
        search_start = time.time()

        # 构建过滤条件
        if book_list == []:
            filter = ''
        else:
            filter = f'array_contains_any(book, {json.dumps(book_list)})' # 三元组检索用这个
            # filter = f'''book in {book_list}'''
        search_params = {
            "metric_type": "COSINE",  # 根据实际类型调整
            "params": {"radius": 0.65}  # 设置阈值
        }
        results = client.search(
            collection_name=collection_name,
            data=[vector],
            output_fields=["index", "tuple", "book", "label", "subject", "relation", "object"],
            limit=top_k,
            filter=filter,
            # search_params=search_params
        )
        search_time = time.time() - search_start
        total_time = time.time() - start_time

        print(f"线程 {thread_name} 完成查询 '{query}': 嵌入时间={embedding_time:.3f}s, 搜索时间={search_time:.3f}s, 总时间={total_time:.3f}s")

        return {
            "query": query,
            "results": results[0],
            "timing": {
                "embedding": embedding_time,
                "search": search_time,
                "total": total_time
            }
        }
    except Exception as e:
        print(f"线程 {thread_name} 查询失败: {e}")
        return {
            "query": query,
            "error": str(e),
            "results": []
        }


def concurrent_search(emb_client, model_name, queries: List[str], book_list: list = [], top_k: int = 5, max_workers: int = 5,
                      milvus_url="http://c-083fddec0b90d74c.milvus.aliyuncs.com:19530",
                      milvus_token="root:GC2023!0814@&^$%#es",
                      db_name="leeman",
                      collection_name="spo") -> Dict[str, Any]:
    """并发执行多个搜索查询"""
    print(f"开始并发查询，查询数量: {len(queries)}, 最大线程数: {max_workers}")
    start_time = time.time()

    # 确保全局连接已建立
    connections.connect(uri=milvus_url, token=milvus_token)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有查询任务
        future_to_query = {executor.submit(search_by_vector, emb_client, model_name, query, book_list, top_k,
                                           milvus_url, milvus_token, db_name, collection_name): query for query in queries}

        # 收集结果
        for future in concurrent.futures.as_completed(future_to_query):
            query = future_to_query[future]
            try:
                data = future.result()
                results.append(data)
            except Exception as e:
                print(f"查询 '{query}' 处理失败: {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "results": []
                })

    total_time = time.time() - start_time
    print(f"所有查询完成，总耗时: {total_time:.3f}秒")

    return results

def get_labels(input_results):
    labels = []
    for i in input_results:
        if 'error' in i.keys():
            pass
        else:
            for j in i['results']:
                label = j['entity']['label']
                if isinstance(label, google._upb._message.RepeatedScalarContainer):
                    labels.extend(list(label)) # 不限定对象格式，会报错
                else:
                    labels.append(label)
    return labels

if __name__ == "__main__":
    # 嵌入模型
    emb_model = "text-embedding-v3"
    emb_api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    emb_key = 'sk-e5ed91a78f424009821dade731c0dffb'
    emb_client = OpenAI(
        api_key=emb_key,
        base_url=emb_api_base,
    )

    # milvus配置
    MILVUS_URI = "http://c-083fddec0b90d74c.milvus.aliyuncs.com:19530"
    MILVUS_TOKEN = "root:GC2023!0814@&^$%#es"
    COLLECTION_NAME = "spo_v2"
    db_name = "leeman"
    # book_list = ["中医儿科学", "内科学"]  # 替换成你的书列表
    book_list = []

    query_list = ['''('下睑红鲜，面部火痤', '表明', '下焦有热或血热')''']


    results = concurrent_search(emb_client, model_name=emb_model, queries=query_list, book_list=book_list, top_k=3, max_workers=len(query_list),
                                milvus_url="http://c-083fddec0b90d74c.milvus.aliyuncs.com:19530",
                                milvus_token="root:GC2023!0814@&^$%#es",
                                db_name="leeman",
                                collection_name=COLLECTION_NAME)

    # 获取label
    labels = get_labels(results)

    # from scipy.sparse.csgraph import csgraph
    print(1)