import itertools
import os
import re
import sys
from typing import Optional, TextIO

import easyocr

MIN_POINTS_PER_LINE = 15
STOP_WORDS = ["CONCLUIDO", "1"]
START_FORMATS = ["^[0-9].*/[0-9].*$", "^[0-9].*"]

# Headers formato unico para la remision de documentos base de la accion en materia civil
rawHeaders = ['EXPEDIENTE', 'NÚM DE SOBRES', 'ACTOR', 'DEMANDADO', 'MOTIVO DE RESGUARDO']
newHeaders = ['EXPEDIENTE', 'ACTOR', 'DEMANDADO', 'MOTIVO DE RESGUARDO', 'PADDING', 'NÚM DE SOBRES']


def separate_by_line(ocr_output: list) -> list:
    return [entry[1] for entry in ocr_output]


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
        if (countItemsLine == 0 or countItemsLine == 4):
            itemLineStr = '' + dataItem
            countItemsLine += 1
        elif (countItemsLine > 0 and countItemsLine <= 3):
            itemLineStr = itemLineStr + "," + dataItem
            countItemsLine += 1
            # print('countItemsLine', countItemsLine)
        else:
            # itemLineStr = itemLineStr + ' /'
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


def filter_chars(line: list[str], chars: dict[str, str]) -> list[str]:
    new_list = line
    for char, repl in chars.items():
        new_list = [element.replace(char, repl) for element in line]
    return new_list


def write_row(file: TextIO, line: list[str]) -> None:
    line = filter_chars(line, {"@": "O", "{": "", "}": "", '"': ''})
    this_line = ",".join(line)
    this_line += "," * (len(newHeaders) - len(line)) + "1" + "\n"
    file.write(this_line)


def create_string_data_2(data: list[str], f: TextIO, page: Optional[int] = 0) -> None:
    local_data = data
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


def get_dir_name(full_path: str) -> str:
    return full_path.split("/")[-1]


def run_all_over_dir(dir: str, reader: easyocr.Reader) -> None:
    files = next(os.walk(dir), (None, None, []))[2]

    file_num = 1
    csv_file_name = dir + "/" + get_dir_name(dir) + ".csv"
    with open(csv_file_name, "w") as f:
        f.write(",".join(newHeaders) + "\n")
        for file in files:
            if file.endswith(".jpeg") or file.endswith(".jpg"):
                f_result = reader.readtext(dir + "/" + file)

                data = separate_by_line(f_result)
                pos = get_nearest_start(data)
                data = data[pos:]

                create_string_data_2(data, f, page=file_num)
                file_num += 1


if __name__ == "__main__":
    # Create an OCR reader object
    reader = easyocr.Reader(['es'])

    # This is the inout dir
    input_dir = "Sobres/122_TERCERO FAMILIAR DE ECATEPEC_2016-2020_T1_SOBRES-20240628T013712Z-001/122_TERCERO FAMILIAR DE ECATEPEC_2016-2020_T1_SOBRES/SOBRES_20231005-105426-038"

    # check input arguments
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]

    local_path = os.path.abspath(__file__).split("\\")[:-1]
    local_path = "/".join(local_path) + "/" + input_dir

    run_all_over_dir(local_path, reader)
