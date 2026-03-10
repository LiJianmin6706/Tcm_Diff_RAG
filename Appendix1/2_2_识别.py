import os
import requests
from tqdm import tqdm
from my_utils.utils import retry_until_success, load_image
from my_utils.detect import table_rec, title_rec
import datetime
import pandas as pd
from my_utils.utils import encode_image, sort_key
from paddleocr import PaddleOCRVL
import json

pipeline = PaddleOCRVL(vl_rec_backend="vllm-server", vl_rec_server_url="http://127.0.0.1:8118/v1")

'''
重要参数
'''
path = 'data/pdf2images'  # 存放识别图片的路径
save_path = 'data/save'
figure_path = 'data/md/figure'
detect_url = 'http://127.0.0.1:5001/detect'
order_url = 'http://127.0.0.1:5002/order'
# ocr_url = "http://127.0.0.1:5003/ocr"
filter_list = ['Title', 'Subtitle', 'Text', 'Figure', 'Figure caption', 'Figure descripition', 'Table',
               'Table descripition', 'Code', 'Code descripition', 'Pseduo code', 'Formula'] # 要提取的标签


# img_paths = [os.path.join(path, j) for j in os.listdir(path)]
img_paths = [os.path.abspath(os.path.join(path, j)) for j in os.listdir(path)]
img_paths = sorted(img_paths, key=sort_key)
dict_list = []
for index, img_path in enumerate(tqdm(img_paths, total=len(img_paths))):
    name = img_path.split('\\')[-1].split('_page')[0]
    file_name = os.path.basename(img_path)
    page = int(img_path.split('/')[-1].split('_page')[1].split('.')[0][1:])

    my_input = {"img_path": img_path, "url": detect_url, "filter_list": filter_list}
    result = requests.post(order_url, json=my_input).json()

    '''
    进行一页的识别
    '''
    for i in result:
        box = i[2:6]
        loc = i[-1]
        if i[0] == 'Figure':
            current = datetime.datetime.now()
            save_name = current.strftime("%Y-%m-%d_%H-%M-%S")
            crop = load_image(img_path, box)
            crop.save(f"{figure_path}/{save_name}.jpg")
            output_str = f'![image-{save_name}](figure/{save_name}.jpg)'

        else:
            image_array = encode_image(img_path, xyxy_coords=box)
            result = pipeline.predict(input=image_array, prompt_label="Table Recognition")
            output_str = result[0].markdown['markdown_texts']
            output_str = output_str.replace('## ', '')
            output_str = output_str.replace('# ', '')
            output_str = output_str.replace('#', '')
            output_str = output_str.replace('\n', '')
            save_name = ''

        result_dict = {'book':name, 'page':page, 'location': loc, 'label': i[0], 'text': output_str, 'save_name': save_name,
                       'file_name':file_name, 'box':str(box)}

        filename = 'data/save/data.jsonl'
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result_dict, ensure_ascii=False) + '\n')

print(1)



