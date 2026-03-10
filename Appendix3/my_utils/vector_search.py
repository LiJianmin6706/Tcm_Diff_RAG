from openai import OpenAI
from typing import List
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import ElasticsearchStore
from elasticsearch import Elasticsearch
from openai import OpenAI
from typing import List
from collections import defaultdict
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class MyEmbeddings(Embeddings):
    def __init__(self, model: str, openai_api_base: str, api_key:str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=openai_api_base)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        result = [i.embedding for i in response.data]
        return result

    def embed_query(self, text: str):
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        result = response.data[0].embedding
        return result

class ES_search:
    def __init__(self, es, index_name, model, api_base, api_key):
        self.es_index_name = index_name
        self.es_db = es
        # self.es_db = Elasticsearch(
        #     "http://es-cn-9lb3cjnbp000m6xzo.public.elasticsearch.aliyuncs.com:9200",
        #     basic_auth=('elastic', 'GC2023!0814@&^$%#es'),
        #     request_timeout=100
        # )
        self.to_embeddings = MyEmbeddings(
            model=model,
            openai_api_base=api_base,
            api_key=api_key
        )
        self.vector_store = ElasticsearchStore(
            embedding=self.to_embeddings,  # 传入嵌入模型
            es_connection=self.es_db,     # 传入 Elasticsearch 客户端
            index_name=self.es_index_name   # 指定索引名称
        )

    async def async_match_tuple(self, query, books, k_num):
        match_range = []  # 不传默认全局搜索
        if books and isinstance(books, list):
            match_range = [{'match': {'metadata.book.keyword': book}} for book in books]
        filter = {
            "terms": {"metadata.book.keyword": books}
        }
        # filter = {
        #     "bool": {
        #         "should": [  # 任意一个条件满足即可
        #             {"term": {"metadata.book.keyword": book}}  # 精确匹配
        #             for book in books
        #         ]
        #     }
        # }
        search_results = self.vector_store.similarity_search_with_score(query, k=k_num, filter=filter)
        return search_results
    #
    def match_tuple(self, query, k_num):
        search_results = self.vector_store.similarity_search_with_score(query, k=k_num)
        return search_results