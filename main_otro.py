import itertools
import os
import re
import sys
import difflib
from typing import Optional, TextIO

import easyocr

MIN_POINTS_PER_LINE = 15
geometry = [
    {"STOP_WORDS": ["CONCLUIDO", "TERMINADO", "INACTIVIDAD"], "SLIDE": 1},
    {"STOP_WORDS": ["SOBRES"], "SLIDE": 2},
    {"STOP_WORDS": ["MERCANTIL", "CIVIL", "A JUICIO"], "SLIDE": 1},
    {"STOP_WORDS": ["EJECUTIVO MERCANTIL", "ESPECIAL DESAHUCIO", "ORDINARIO CIVIL", "CONSIGNA PAGO"], "SLIDE": 2},
    {"STOP_WORDS": ["EJEC. MERC.", "ESPECIAL DE DESAHUCIO", "ORD. CIV.", "CONSIGNA", "MED.PRE.ESP.DESH.",
                    "ORD. CIV. RES. CONT.", "JURIS. VOL.", "PRC.JUD.NO.CONTENC."], "SLIDE": 2},
    {"STOP_WORDS": ["FALTA DE ESPACIO"], "SLIDE": 1},
    {"STOP_WORDS": ["PENSION ALIMENTICIA", "DIVORCIO NECESARIO", "SUCESION INTESTAMENTARIA", "ORDINARIO CIVIL",
                    "JURISDICCION VOLUNTARIA", "DIVORCIO VOLUNTARIO", "PETICION DE HERENCIA",
                    "PERDIDA DE LA PATRIA POT", "SUCESORIO TESTAMENTARIO", "AUTORIZACION PARA VENDER",
                    "GUARDA Y CUSTODIA", "RECTIFICACION DE ACTA", "CANCEL DE P. ALIM", "CANCELACION DE PENSION",
                    "PRESUNCION DE MUERTE", "CUMPLIMIENTO DE CONVENIO", "RED. DE PEN ALIM", "MODIFICACION DE CONVENIO"],
     "SLIDE": 3},
]
STOP_WORDS = None
SLIDE = None
START_FORMATS = ["^[0-9].*/[0-9].*$", "^[0-9].*$"]

# Headers formato unico para la remision de documentos base de la accion en materia civil
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


def find_endswith(data, ending) -> int:
    pos = 0
    for dataItem in data:
        if dataItem.endswith(ending):
            return pos
        pos += 1
    raise ValueError("Value does not end with ending")


def get_nearest_stop(data: list[str]) -> int:
    positions = []
    for word in STOP_WORDS:
        print(word)
        try:
            pos = find_endswith(data, word)
        except ValueError:
            pos = 10000
        print(pos)
        positions.append(pos)
    return min(positions)


def get_nearest_stop_2(data: list[str]) -> int:
    pos = 0
    for dataItem in data:
        res = difflib.get_close_matches(dataItem, STOP_WORDS)
        if res:
            return pos + SLIDE
        pos += 1
    return pos


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
                if pos > 1:
                    return pos - 1
            pos += 1
    raise ValueError("Regex did not find anything.")


def write_row(file: TextIO, line: list[str]) -> None:
    for element in line:
        if "@" in element:
            element.replace("@", "")
    this_line = ",".join(line)
    this_line += "," * (len(newHeaders) - len(line)) + "1" + "\n"
    file.write(this_line)


def create_string_data_2(data: list[str], f: TextIO, page: Optional[int] = 1) -> None:
    local_data = data
    while len(local_data) > 0:
        # pos = get_nearest_stop(local_data)
        pos = get_nearest_stop_2(local_data)
        print("pos: ", pos)
        if pos > 5:
            old_pos = pos
            try:
                pos = get_nearest_start(local_data)
            except ValueError:
                pos = 6
            if pos:
                items = local_data[:pos]
                local_data = local_data[pos:]
            else:
                items = [f"Fin de pagina numero: {page}"]
                local_data = []
        else:
            items = local_data[:pos + 1]
            local_data = local_data[pos + 1:]
        write_row(f, items)
    items = [f"Fin de pagina numero: {page}"]
    write_row(f, items)


def run_all_over_dir(dir: str, reader: easyocr.Reader) -> None:
    files = next(os.walk(dir), (None, None, []))[2]

    file_num = 1
    filename = dir + "/" + dir.split("/")[-1] + ".csv"
    with open(filename, "w") as f:
        f.write(",".join(newHeaders) + "\n")
        for file in files:
            if file.endswith(".jpg") or file.endswith(".jpeg"):
                f_result = reader.readtext(dir + "/" + file)

                data = separate_by_line(f_result)[0]
                try:
                    pos = get_nearest_start(data)
                except ValueError:
                    data = []
                else:
                    data = data[pos:]

                create_string_data_2(data, f, page=file_num)
                file_num += 1


if __name__ == "__main__":
    # Create an OCR reader object
    reader = easyocr.Reader(['es'])

    # This is the input dir
    input_dir = "Sobres4/C24.2_1o FAMILIAR DE ECATEPEC_2012_SOBRES-20240716T204457Z-001/C24.2_1o FAMILIAR DE ECATEPEC_2012_SOBRES/SOBRES_20231013-154553-168"
    STOP_WORDS = geometry[6]["STOP_WORDS"]
    SLIDE = geometry[6]["SLIDE"]

    # check input arguments
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]

    local_path = os.path.abspath(__file__).replace("\\", "/")
    local_path = local_path.split("/")[:-1]
    local_path = "/".join(local_path) + "/" + input_dir

    run_all_over_dir(local_path, reader)
