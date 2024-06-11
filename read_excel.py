from img2table.document import Image

# Instantiation of the image
img = Image(src="20231009-181355-189-01.jpg")

# Table identification
imgage_tables = img.extract_tables()

# Result of table identification
print(imgage_tables)
