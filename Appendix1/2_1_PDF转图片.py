import fitz #pip install PyMuPDF
import os
from tqdm import tqdm

def pdf2img(path, save_path, ratio):
    '''
    :param path: 存放pdf的文件夹
    :param save_path: 存放转化好的图片的文件夹
    :return: 将每页pdf转成图片
    '''
    pdf_files = [os.path.join(path,j) for j in os.listdir(path)]

    for pdf_file in tqdm(pdf_files):
        filename_list = os.path.basename(pdf_file).split('.pdf')
        # filename = max(filename_list)
        filename = filename_list[0]
        doc = fitz.open(pdf_file)

        for i in range(doc.page_count):
            page = doc.load_page(i)
            zoom_x = ratio # 书的可能要设置大一些，文献设置为5
            zoom_y = ratio
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom_x, zoom_y))
            output_name = f"{filename}_page_{i+1}.jpg"
            output_file = os.path.join(save_path, output_name)
            pix.save(output_file)

source_path = 'data/book' # 选择书本还是文献
images_path = 'data/pdf2images'

# delete_files(images_path)
pdf2img(source_path, images_path, ratio=2)