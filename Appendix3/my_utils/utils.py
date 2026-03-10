from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def fix_json(json_str):
    # pattern = r"json\n([\s\S]*?)\n"
    cleaned_str = json_str.strip('` \n').replace('json', '')
    a = '''“'''
    cleaned_str.replace('''“''', '''"''')
    data = eval(cleaned_str)
    return data


def second_filter(model, query, kgs):
    # model是大模型的名称
    # kgs是一个列表，里面的元素是metadata字典

    api_base = "http://47.99.155.171:3000/v1"
    api_key = "sk-ll0CVS7hnnA6R4iGC65a44D8AaB447B995D68aE4Fa6f7637"
    llm = ChatOpenAI(base_url=api_base, api_key=api_key, model=model, max_retries=4)
    '''
    构建链
    '''
    template = '''
    以下是检索到的文档: \n\n {context} \n\n
    这是用户的问题: {query} \n    
    你需要评估用户的问题是否和文档相关. \n
    以下是要求：
    - 如果文档和问题相关，有助于回答问题，输出yes
    - 如果文档和问题相关性不高，则输出no
    - 只输出一个二分类的评分 'yes', 'no'
    - 不允许输出其他内容
    '''
    # - 如果用户输入的是一段病历，检索到的文本需要有助于对其中的症状做出解释、诊断、治疗，那么只要有一点帮助则可以认为是相关文档，输出yes的要求更宽松
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你需要判断文档内容是否能够回答问题"),
        ("user", template)
    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    chain_list = []
    for kg in kgs:
        chain_list.append({"query": query, "context": str(kg)})
    output = chain.batch(chain_list)
    filter_docs = []
    for index, i in enumerate(output):
        if i == 'yes':
            filter_docs.append(kgs[index])
    return filter_docs