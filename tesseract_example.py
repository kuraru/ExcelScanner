import pytesseract

# Perform OCR on an image
text = pytesseract.image_to_string("20231009-181355-189-01.jpg")

print(text)
