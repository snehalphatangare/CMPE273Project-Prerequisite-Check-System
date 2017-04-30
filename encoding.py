import builtins

original_open = open
def bin_open(filename, mode='rb'):       # note, the default mode now opens in binary
    return original_open(filename, mode)

from PIL import Image
import pytesseract

image_file = '/Users/Abhishek/Sem1Projects/CMPE273Project/python-opencv-ocr-master/Unknown.jpg'
img = Image.open(image_file)

try:
    builtins.open = bin_open
    bts = pytesseract.image_to_string(img)
finally:
    builtins.open = original_open

print(str(bts))