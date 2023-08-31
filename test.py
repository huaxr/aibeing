# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com

import pytesseract
from PIL import Image
# Open image file
img = Image.open('/usr/share/nginx/html/docs/test.png')
# Use pytesseract to do OCR on the image
text = pytesseract.image_to_string(img)
print(text)