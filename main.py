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

def removeHeaders(headers: list, data: list):
    for header in headers:
        data.remove(header)
    return data

def create_string_data(data: list):
    itemLineStr = ''
    countItemsLine = 0
    f = open("data.csv", "w")
    for dataItem in data:
        print(dataItem)
        if(countItemsLine == 0 and countItemsLine == 4):
            itemLineStr = '' + dataItem
            countItemsLine += 1
        elif(countItemsLine > 0 and countItemsLine <= 3):
            itemLineStr = itemLineStr + "," + dataItem
            countItemsLine += 1 
            #print('countItemsLine', countItemsLine)
        else:
            #itemLineStr = itemLineStr + ' /'
            f.write(f"{itemLineStr}\n")
            countItemsLine = 0
            itemLineStr = ''
        print(itemLineStr)
    f.close()

# Create an OCR reader object
reader = easyocr.Reader(['es'])

# Read text from an image
result = reader.readtext('20231009-181355-189-01.jpg')

# Print the extracted text
#for detection in result:
    #print(detection[0], detection[1], detection[2])
    #print('detection%', detection)

lines = separate_by_line(result)
data = lines[0]
#print(data)

header = data[0:14]
lastIndex = (len(data) + 1)
#print(lastIndex)
rawData = data[15:lastIndex]
#print(header)
#print(rawData)

#Headers formato unico para la remision de documentos base de la accion en materia civil
rawHeaders =['EXPEDIENTE', 'NÚM DE SOBRES', 'ACTOR', 'DEMANDADO', 'MOTIVO DE RESGUARDO']
newRawData = removeHeaders(rawHeaders, rawData)
c = open('newRawData.txt', 'w')
c.write(','.join(newRawData))
c.close()
#print(newRawData)
create_string_data(newRawData)






