# Rename files in directory so it comply with file 001.jpg, file 002.jpg and so on
# Note that original format is something like: SOBRES_20231009-17582-186 conv 1.jpg
# and the expected output must be: SOBRES_20231009-17582-186 conv 001.jpg since there
# are 173 files in the directory so we have to keep 3 digit numbers.

import os


def get_all_files(fullpath_dir: str) -> list:
    _, _, files = next(os.walk(fullpath_dir))
    return files


def get_amount_of_digits_in_number(num: int) -> int:
    digits = 0
    l_num = num
    while l_num > 0:
        l_num //= 10
        digits += 1
    return digits


def set_num_to_digits(str_num: str, digits: int) -> str:
    actual_len = len(str_num)
    if (digits - actual_len) > 0:
        filling = "0" * (digits - actual_len)
        return f"{filling}{str_num}"
    return str_num


def rename_files(fullpath_dir: str) -> None:
    files = get_all_files(fullpath_dir)
    files = files.sort()
    amount = len(files)
    digits = get_amount_of_digits_in_number(amount)
    for file in files:
        if file.endswith(".jpeg") or file.endswith(".jpg"):
            back_fn = file.split(" ")[0]
            front_fn = " ".join(file.split(" ")[1:])
            str_number = front_fn.split(".")[0].split(" ")[1]
            back_fn += " conv"
            extension = front_fn.split(".")[1]
            try:
                num = int(str_number)
            except ValueError as ve:
                print("element is not possible to convert to number")
                raise ve
            new_num = set_num_to_digits(str_number, digits)
            new_fn = f"{back_fn} {new_num}.{extension}"
            print(fullpath_dir)
            print(file)
            print(new_fn)
            if new_fn != file:
                os.rename(fullpath_dir + "/" + file, fullpath_dir + "/" + new_fn)


if __name__ == '__main__':
    fullpath_dir = "Sobres/130_NOVENO FAMILIAR DE ECATEPEC_2016-2020_T2_SOBRES-20240701T221821Z-001/130_NOVENO FAMILIAR DE ECATEPEC_2016-2020_T2_SOBRES/SOBRES_20231010-131346-104"
    rename_files(fullpath_dir)
