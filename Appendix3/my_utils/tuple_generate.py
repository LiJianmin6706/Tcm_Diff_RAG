from openai import OpenAI
from my_utils.utils import fix_json
import os


def tuple_generation_fun(input_text, model, api_base, api_key):
    prompt = f'''
    以下是问题
    病患突发急性症状，表现为高热、口渴难耐，面部潮红且眼睛充血，尿液偏黄，大便干结，舌苔呈现黄色。其发病机理是（）
    'A': '阳盛格阴', 'B': '阴盛格阳', 'C': '阳盛伤阴', 'D': '阳损及阴', 'E': '阳热偏盛'
    以下是推理所需要的三元组：
    [
    ('阳热偏盛', '属于', '实热证候'),
    ('阳热偏盛', '表现为', '高热'),
    ('阳热偏盛', '表现为', '面红目赤'),
    ('阳热偏盛', '表现为', '口渴'),
    ('阳热偏盛', '表现为', '尿黄便干'),
    ('阳热偏盛', '表现为', '舌苔黄'),
    ('阳盛格阴', '表现为', '真热假寒'),
    ('阳损及阴', '属于', '阳虚及阴的虚证'),
    ('阳盛伤阴', '可能导致', '阴液损伤'),
    ('阴盛格阳', '表现为', '阴寒内盛'),
    ('阴盛格阳', '表现为', '虚阳外越')
    ]
    
    这是新的问题
    {input_text}
    - 请你模仿以上例子，输出与问题相关，推理问题最终答案所需要的三元组，
    - 三元组以列表的形式输出，三元组必须与问题高度相关，能推导出问题的最终答案
    - 只输出列表，不允许输出其他无关内容，注意内容、安全声明等
    '''
    messages = [{"role": "system", "content": "你是一个医学推理专家，擅长从问题中推导出思考的三元组过程"},
                {"role": "user", "content":prompt}
                ]

    client = OpenAI(api_key=api_key, base_url=api_base)
    completion = client.chat.completions.create(
        model=model, # ERNIE-4.0-8K，ERNIE-3.5-8K，ERNIE-4.0-Turbo-128K, qwen-turbo, glm-4, glm-3-turbo
        temperature=0,
        messages=messages
    ).choices[0].message.content
    output = fix_json(completion)
    return output


def tuple_generation_fun(input_text, model, api_base, api_key):
    prompt = f'''
    以下是问题
    病患突发急性症状，表现为高热、口渴难耐，面部潮红且眼睛充血，尿液偏黄，大便干结，舌苔呈现黄色。其发病机理是（）
    'A': '阳盛格阴', 'B': '阴盛格阳', 'C': '阳盛伤阴', 'D': '阳损及阴', 'E': '阳热偏盛'
    以下是推理所需要的三元组：
    [
    ('阳热偏盛', '属于', '实热证候'),
    ('阳热偏盛', '表现为', '高热'),
    ('阳热偏盛', '表现为', '面红目赤'),
    ('阳热偏盛', '表现为', '口渴'),
    ('阳热偏盛', '表现为', '尿黄便干'),
    ('阳热偏盛', '表现为', '舌苔黄'),
    ('阳盛格阴', '表现为', '真热假寒'),
    ('阳损及阴', '属于', '阳虚及阴的虚证'),
    ('阳盛伤阴', '可能导致', '阴液损伤'),
    ('阴盛格阳', '表现为', '阴寒内盛'),
    ('阴盛格阳', '表现为', '虚阳外越')
    ]

    这是新的问题
    {input_text}
    - 请你模仿以上例子，输出与问题相关，推理问题最终答案所需要的三元组，
    - 三元组以列表的形式输出，三元组必须与问题高度相关，能推导出问题的最终答案
    - 只输出列表，不允许输出其他无关内容，注意内容、安全声明等
    '''
    messages = [{"role": "system", "content": "你是一个医学推理专家，擅长从问题中推导出思考的三元组过程"},
                {"role": "user", "content": prompt}
                ]

    client = OpenAI(api_key=api_key, base_url=api_base)
    completion = client.chat.completions.create(
        model=model,  # ERNIE-4.0-8K，ERNIE-3.5-8K，ERNIE-4.0-Turbo-128K, qwen-turbo, glm-4, glm-3-turbo
        temperature=0,
        messages=messages
    ).choices[0].message.content
    output = fix_json(completion)
    return output

if __name__ == "__main__":
    api_base = "http://47.99.155.171:3000/v1"
    api_key = 'sk-ll0CVS7hnnA6R4iGC65a44D8AaB447B995D68aE4Fa6f7637'
    model = "ERNIE-4.0-Turbo-128K"
    input_text = '''
    患者性别男，年龄31岁，主诉：反复咳嗽、发热1年，症状表现现不怕风冷，汗不多，紧运动出汗，汗后吹风易感冒，汗后凉，手脚自觉偏凉。无口干口苦，无心慌胸闷，无头晕耳鸣头痛，无四肢酸疼。上周痰黄，现偶尔有痰，偏白，痰易咳。不发烧时四肢皮肤痒，发烧时不痒，皮肤偏干，痒时皮肤无红色丘疹。纳可，无腹凉，无腹胀。既往喜冷饮，现喜饮热，睡觉一定要盖肚子。大便每日2-3次，不干不稀，小便可，无灼热，夜偶尔0-1（饮多时）。眠可，无梦。脉浮弦数，舌淡紫红嫩，苔黄白腻边齿痕，下睑红鲜，面部火痤，腹薄拘，下肢甲错，抓痕，手微潮微凉。
    请给出中医证候的诊断
    '''
    output_tuple = tuple_generation_fun(input_text, model, api_base, api_key)


    print(1)