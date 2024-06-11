import easyocr

MIN_POINTS_PER_LINE = 15


def separate_by_line(ocr_output: list) -> list:
    last_y = 0
    lines = []
    line = []
    for entry in ocr_output:
        current_y = entry[0][0][1]
        if last_y - current_y >= MIN_POINTS_PER_LINE:
            if len(line):
                lines.append(line)
            line = []
            last_y = current_y
        line.append(entry[1])
    if len(line):
        lines.append(line)
    return lines


# Create an OCR reader object
reader = easyocr.Reader(['es'])

# Read text from an image
result = reader.readtext('20231009-181355-189-01.jpg')

# Print the extracted text
for detection in result:
    print(detection[0], detection[1], detection[2])

lines = separate_by_line(result)
for line in lines:
    print(line)
