# encoding=utf8

import io
import sys

import pyocr
import pyocr.builders
from PIL import Image as PI
from wand.image import Image

import chardet
#import icu

#reload(sys)
#sys.setdefaultencoding('utf8')



#PYTHONIOENCODING=utf-8
try:
    import wand.api
except ImportError:
    pass
sys.modules['wand._api'].load_library()




tool = pyocr.get_available_tools()[0]
lang = tool.get_available_languages()[1]

req_image = []
final_text = []

image_pdf = Image(filename="/Users/Abhishek/Sem1Projects/CMPE273Project/python-opencv-ocr-master/chocolate.pdf", resolution=300)
image_jpeg = image_pdf.convert('jpeg')


for img in image_jpeg.sequence:
    img_page = Image(image=img)
    req_image.append(img_page.make_blob('jpeg'))


for img in req_image: 
    txt = tool.image_to_string(
        PI.open(io.BytesIO(img)),
        lang=lang,
        builder=pyocr.builders.TextBuilder()
    )
    #str(txt).decode(encoding='UTF-8',errors='strict')
   # print txt
    # =  txt.encode('utf-8')

    encoding = chardet.detect(txt)['encoding']
    new_coding='UTF-8'
    if new_coding.upper() != encoding.upper():
        txt = txt.decode(encoding, txt).encode(new_coding)

    print txt


    #s = txt.decode('ascii', 'ignore')
    final_text.append(txt)

print final_text
