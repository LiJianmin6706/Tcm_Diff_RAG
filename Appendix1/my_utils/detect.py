import requests
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
import time
from functools import wraps
from openai import AzureOpenAI
import hashlib
import colorsys

def get_box(url, path, filter_list):
    '''
    :param url: youlov的后台链接
    :param path: 图片路径
    :param filter_list: 要筛选出的标签，如只想筛选出Text，Title等
    :return: [类别, 置信度, 坐标*4, 阅读顺序]
    '''
    image_data = open(path, "rb").read()
    response = requests.post(url, files={"image": image_data}, timeout=(40, 40)).json()
    response = response['result']
    response['label_name'] = [response['lables'][str(int(i))] for i in response['classes']] # 增加一个标签名
    xmin_list = [i[0] for i in response['boxes']]
    ymin_list = [i[1] for i in response['boxes']]
    xmax_list = [i[2] for i in response['boxes']]
    ymax_list = [i[3] for i in response['boxes']]
    result = [[x, y, xmin, ymin, xmax, ymax] for x, y, xmin, ymin, xmax, ymax in zip(response['label_name'], response['conf'], xmin_list, ymin_list, xmax_list, ymax_list)]


    result = [i for i in result if i[2] >= 0.5] # 筛选置信度大于0.5的
    result = [i for i in result if i[0] in filter_list] # 筛选出选定的标签
    for i in result:
        if i[0]=='Subtitle':
            # i['ymin'] = i['ymin']-5
            i[3] = i[3]-5

    return result

def label_to_color(label: str):
    """
    基于标签生成稳定且可区分的BGR颜色。
    - 用 md5(label) 获取 0~1 的 hue
    - 固定饱和度与明度，避免过浅或过深
    """
    # 1) 稳定哈希到 [0, 1)
    h_hex = hashlib.md5(label.encode('utf-8')).hexdigest()
    h_int = int(h_hex[:8], 16)                 # 取前8位更分散
    h = (h_int % 360) / 360.0                  # hue ∈ [0,1)

    # 2) HSV -> RGB (0-1 浮点)
    s = 0.75
    v = 0.95
    r, g, b = colorsys.hsv_to_rgb(h, s, v)

    # 3) 转为 OpenCV 的 BGR 0-255
    return (int(b*255), int(g*255), int(r*255))




def retry(max_retries=3, delay=1, allowed_exceptions=(Exception,)):
    """通用重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    retries += 1
                    if retries >= max_retries:
                        raise  # 达到重试次数后抛出原异常
                    print(f"Retry {retries}/{max_retries} for {func.__name__} due to: {str(e)}")
                    time.sleep(delay * retries)  # 指数退避
            return None  # 或返回默认值
        return wrapper
    return decorator

def table_rec(img_path, box):
    def encode_image(image_path, xyxy_coords=None):
        # 统一使用原图或裁剪后的图片
        image = Image.open(image_path)

        # 处理裁剪逻辑
        if xyxy_coords:  # 自动过滤空列表/None等假值
            processed_image = image.crop(tuple(xyxy_coords))
        else:
            processed_image = image

        # 统一处理图片模式（确保兼容JPEG）
        if processed_image.mode in ('RGBA', 'LA', 'P'):
            processed_image = processed_image.convert('RGB')

        # 统一转为字节流
        img_byte_arr = BytesIO()
        processed_image.save(img_byte_arr, format='JPEG', quality=95)  # 保持高质量

        return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    base64_image = encode_image(img_path, xyxy_coords=box)

    # key = 'sk-ll0CVS7hnnA6R4iGC65a44D8AaB447B995D68aE4Fa6f7637'
    # url = 'http://47.99.155.171:3000/v1'
    url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    key = 'sk-e5ed91a78f424009821dade731c0dffb'
    client = OpenAI(api_key=key, base_url=url, max_retries=5)
    model_name = 'qwen-vl-max'  # glm-4v, qwen-vl-max, qwen-vl-plus, Qwen2-72B-vl
    sys = '你是一个表格识别专家，能将图片中的表格转成markdown格式的表格'
    prompt = '''请把图片中的表格或列表识别，并转成markdown格式的表格，只输出一个表格，除了表格之外，不要输出其他无关内容，以下是输出格式示例：

    |                | 吸气性呼吸困难                                               | 呼气性呼吸困难                            | 混合性呼吸困难                                               |
    | -------------- | ------------------------------------------------------------ | ----------------------------------------- | ------------------------------------------------------------ |
    | 病因           | 咽喉部及气管上段的阻塞性 疾病，如咽后脓肿、喉炎、肿 瘤、异物、白喉、声带瘫痪等 | 小支气管阻塞性疾病，如 支气管哮喘、肺气肿 | 气管中、下段或上、下呼吸 道同时患阻塞性疾病，如 喉气管支气管炎、气管 肿瘤 |
    | 呼吸深度与频率 | 吸气期延长，吸气运动增强， 呼吸频率基本不变或减慢            | 呼气期延长，呼气运动增 强，吸气运动略增强 | 吸气与呼气均增强                                             |
    '''

    # 提交信息至GPT4o
    response = client.chat.completions.create(
        model=model_name,  # 选择模型
        messages=[
            {
                "role": "system",
                "content": sys
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ]
            }
        ],
        stream=False,
    )

    answer = response.choices[0].message.content
    return answer

def title_rec(img_path, box):
    def encode_image(image_path, xyxy_coords=None):
        # 统一使用原图或裁剪后的图片
        image = Image.open(image_path)

        # 处理裁剪逻辑
        if xyxy_coords:  # 自动过滤空列表/None等假值
            processed_image = image.crop(tuple(xyxy_coords))
        else:
            processed_image = image

        # 统一处理图片模式（确保兼容JPEG）
        if processed_image.mode in ('RGBA', 'LA', 'P'):
            processed_image = processed_image.convert('RGB')

        # 统一转为字节流
        img_byte_arr = BytesIO()
        processed_image.save(img_byte_arr, format='JPEG', quality=95)  # 保持高质量

        return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    base64_image = encode_image(img_path, xyxy_coords=box)

    # client = AzureOpenAI(
    #     api_key="0e1764222461427ba8e533185b7691c2",
    #     api_version="2023-07-01-preview",
    #     azure_endpoint="https://openai-gc-us2.openai.azure.com/"
    # )
    # model_name = "gpt-4o-mini"


    url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    key = 'sk-e5ed91a78f424009821dade731c0dffb'
    client = OpenAI(api_key=key, base_url=url, max_retries=5)
    model_name = 'qwen-vl-max'  # glm-4v, qwen-vl-max, qwen-vl-plus, Qwen2-72B-vl
    sys = '你是一个OCR识别专家，能将图片中的文字识别'
    prompt = '请你识别图片中的文字，直接输出识别后的文字，不允许输出其他不相关的文字。不允许输出 图片中的文字是：'

    # 提交信息至GPT4o
    response = client.chat.completions.create(
        model=model_name,  # 选择模型
        messages=[
            {
                "role": "system",
                "content": sys
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ]
            }
        ],
        stream=False,
    )

    answer = response.choices[0].message.content
    return answer

if __name__ == "__main__":
    img_path = r'F:\示范项目\76_新版面识别全流程\data/已完成/2025-4-25人教版第10/pdf2images/09. 生物化学与分子生物学（第10版）n_page_312.jpg'
    # box怎么来
    box = [162.9798583984375, 592.7476196289062, 665.4732055664062, 627.7578735351562]
    answer = title_rec(img_path, box)
    print(answer)
