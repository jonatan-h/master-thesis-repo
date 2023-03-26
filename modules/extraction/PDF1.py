# from modules.extraction.PDFMiner import extract_raw_text
import re

from modules.extraction.PDFPlumber import extract_raw_text, extract_tables
import tabula
import pandas
from modules.extraction.TextParser import parse_pdf1_text


result_viewers = 0


def is_valid(table):
    if not table or len(table) < 2:
        return False

    peak_flag = False
    anvil_flag = False
    position_flag = False
    result_flag = False

    for i in range(0, 2):
        for col_name in table[i]:
            if re.search("Peak", str(col_name)):
                peak_flag = True
            elif re.search("Anvil", str(col_name)):
                anvil_flag = True
            elif re.search("Position", str(col_name)):
                position_flag = True
            elif re.search("PASS", str(col_name)):
                result_flag = True

    return peak_flag and anvil_flag and position_flag and result_flag


def count_result_viewers(text):
    counter = 0
    for page in text:
        matches = re.findall(r"Results\s*Viewer", page)
        counter += len(matches)
    global result_viewers
    result_viewers = counter


def extract_text(path):
    text = extract_raw_text(path)
    count_result_viewers(text)

    text_data = parse_pdf1_text(text)

    model_match = re.search(r"(CYCLING|SNOW)[\\/][\w\s+°]+", path)
    if model_match:
        model = re.sub(r"(CYCLING|SNOW)[\\/]", "", model_match[0])

        i = 0
        while i in text_data:
            text_data[i]["Model"] = model
            i += 1

    helmet_type = re.search(r"(CYCLING|SNOW)", path)
    if helmet_type:
        i = 0
        while i in text_data:
            text_data[i]["Helmet Type"] = helmet_type[0]
            i += 1

    stage_of_testing = re.search(r"(Development|BatchTesting|Certificates)", path)
    if stage_of_testing:
        i = 0
        while i in text_data:
            text_data[i]["Stage of Testing"] = stage_of_testing[0]
            i += 1

    return text_data


def extract_table_data(path):
    tables = extract_tables(path)

    valid_tables = []
    # Look for valid table(s), skipping over the leading result viewers
    for i in range(result_viewers, len(tables)):
        if is_valid(tables[i]):
            valid_tables.append(tables[i])

    return valid_tables


def extract_pdf1(path):
    text_data = extract_text(path)
    table_data = extract_table_data(path)

    return {"text_data": text_data, "table_data": table_data}
