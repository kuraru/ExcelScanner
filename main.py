import itertools
import os
import re
from typing import Optional, TextIO

import easyocr

MIN_POINTS_PER_LINE = 15
STOP_WORDS = ["CONCLUIDO"]
START_FORMATS = ["^[0-9].*/[0-9].*$"]

#Headers formato unico para la remision de documentos base de la accion en materia civil
rawHeaders = ['EXPEDIENTE', 'NÚM DE SOBRES', 'ACTOR', 'DEMANDADO', 'MOTIVO DE RESGUARDO']
newHeaders = ['EXPEDIENTE', 'ACTOR', 'DEMANDADO', 'MOTIVO DE RESGUARDO', 'PADDING', 'NÚM DE SOBRES']


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
        if(countItemsLine == 0 or countItemsLine == 4):
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


def get_nearest_stop(data: list[str]) -> int:
    positions = []
    for word in STOP_WORDS:
        print(word)
        pos = data.index(word)
        print(pos)
        positions.append(pos)
    return min(positions)


def get_nearest_start(data: list[str]) -> int:
    positions = []
    for format in START_FORMATS:
        print(format)
        pos = 0
        for string in data:
            if pos == 0:
                pos += 1
                continue
            if re.search(format, string):
                return pos
            pos += 1
    raise ValueError("Regex did not find anything.")


def write_row(file: TextIO, line: list[str]) -> None:
    this_line = ",".join(line)
    this_line += "," * (len(newHeaders) - len(line)) + "1" + "\n"
    file.write(this_line)


def create_string_data_2(data: list[str], page: Optional[int]=0) -> None:
    local_data = data
    with open("data.csv", "w") as f:
        f.write(",".join(newHeaders) + "\n")
        while len(local_data) > 0:
            try:
                pos = get_nearest_stop(local_data)
                print("pos: ", pos)
                if pos > 5:
                    pos = get_nearest_start(local_data)
                    if pos:
                        items = local_data[:pos]
                        local_data = local_data[pos:]
                    else:
                        items = [f"Fin de pagina numero: {page}"]
                        local_data = []
                else:
                    items = local_data[:pos + 1]
                    local_data = local_data[pos + 1:]
            except ValueError:
                items = [f"Fin de pagina numero: {page}"]
                local_data = []
            write_row(f, items)


def run_all_over_dir(dir: str, reader: easyocr.Reader) -> None:
    files = next(os.walk(dir), (None, None, []))[2]

    file_num = 0
    for file in files:
        f_result = reader.readtext(file)

        lines = separate_by_line(f_result)
        data = lines[0]


if __name__ == "__main__":
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
    # lastIndex = (len(data) + 1)
    #print(lastIndex)
    rawData = data[15:-1]
    #print(header)
    #print(rawData)

    newRawData = removeHeaders(rawHeaders, rawData)
    newRawData = list(itertools.filterfalse(lambda x: x == "", newRawData))
    newRawData = [element.replace(",", "") for element in newRawData]
    # print(newRawData)
    c = open('newRawData.txt', 'w')
    c.write(','.join(newRawData))
    c.close()
    create_string_data_2(newRawData, page=0)
