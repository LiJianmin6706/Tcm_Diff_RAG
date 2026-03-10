import re
import time
from PIL import Image
import os
import cv2
import numpy as np

def latex_to_markdown(text):
    # 预处理：合并换行、去除多余空格
    text = re.sub(r'\n+', '\n', text).strip()

    # 定义转换规则
    rules = [
        # 处理标题（支持多行标题）
        (r'\\title{\n*(.*?)\n*}', lambda m: f'# {m.group(1).strip()}\n'),
        # 处理无编号章节（支持二级/三级标题判断）
        (r'\\section\*{\s*([^}]+?)\s*}',
         lambda m: f'## {m.group(1)}' if "(" not in m.group(1) else f'### {m.group(1)}'),
        # 处理带编号的列表项（支持多级列表）
        (r'(\d+)\.\s+(.*)', lambda m: ' ' * 4 * (m.group(1).count('.') + 1) + f'1. {m.group(2)}'),
        # 处理特殊符号【】
        (r'【(.*?)】', r'​**​\1​**​'),
        # 处理问答结构
        (r'(\d+)\.\s+(.*?)\n答：(.*?)(?=\n\d+\.|\Z)',
         lambda m: f'### {m.group(1)}. {m.group(2)}\n{m.group(3)}\n'),
        # 处理普通段落换行
        (r'(?<!\n)\n(?!\n)', '\n\n')
    ]

    # 按顺序应用转换规则
    for pattern, replacement in rules:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    return text

def retry_until_success(func, *args, **kwargs):
    i = 0
    while i<=2:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            i+=1
            print(f"An error occurred: {e}. Retrying {i}...")
            time.sleep(2)

def load_image(image_path, box=[]):
    # 打开图像
    image = Image.open(image_path)


    # 解析XYXY坐标
    if box!=[]:
        img_width, img_height = image.size
        xyxy = box
        x1, y1, x2, y2 = xyxy

        # 将浮点坐标转为整数（四舍五入）
        x1 = int(round(x1))
        y1 = int(round(y1))
        x2 = int(round(x2))
        y2 = int(round(y2))

        # 确保坐标不越界
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(img_width, x2)
        y2 = min(img_height, y2)

        # 截取区域
        if x1 >= x2 or y1 >= y2:
            raise ValueError("Invalid coordinates: region is empty or negative.")

        cropped = image.crop((x1, y1, x2, y2))
    else:
        cropped = image
    return cropped

def adjust_list_length(lst, num):
    if len(lst) < num:
        # 如果列表长度小于5，则用None或其他指定值填充至5个元素
        lst.extend([lst[-1]] * (num - len(lst)))
    elif len(lst) > num:
        # 如果列表长度大于5，则移除多余的元素
        del lst[num:]
    return lst


def cv2_imwrite_chinese_path(path, img):
    try:
        # 获取文件扩展名
        ext = os.path.splitext(path)[1]
        # 使用 imencode 编码图像
        ret, buf = cv2.imencode(ext, img)
        if ret:
            with open(path, 'wb') as f:
                buf.tofile(f)
            return True
    except Exception as e:
        print(f"保存失败: {e}")
    return False

def imread_chinese_path(img_path):
    """读取中文路径图像"""
    try:
        # 以二进制方式读取文件
        with open(img_path, 'rb') as f:
            img_data = np.frombuffer(f.read(), dtype=np.uint8)
        # 使用 imdecode 解码图像
        img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"读取图像失败: {e}")
        return None

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

    # 转为数组形式
    image_array = np.array(processed_image)
    return image_array

def sort_key(path):
    # 取出文件名
    filename = os.path.basename(path)
    # 提取书名（_page 之前的部分）
    book_name = filename.split('_page')[0]
    # 提取页码
    page_match = re.search(r'page_(\d+)', filename)
    page_num = int(page_match.group(1)) if page_match else 0
    return (book_name, page_num)