from modules.extraction.PDFPlumber import extract_raw_text, extract_tables
from modules.extraction.TextParser import parse_pdf3_text
import re
from util import get_helmet_type


def condition_match(string):
    match = re.search("Condition", str(string))
    return match


def anvil_match(string):
    """Anvil is not always included and is thus not a requirement to identify the table"""
    match = re.search("Anvil", str(string))
    return match


def imp_match(string):
    match = re.search(r"(Impact|Test)\s+[Ss]ite", str(string))
    return match


def peak_match(string):
    match = re.search(r"Peak(\s+[Aa]cceleration)?", str(string))
    return match


def result_match(string):
    match = re.search("Result", str(string))
    return match


def is_table(table):
    """Check if table qualifies as a table that should be processed (there may be multiple)"""
    if not table:
        return False

    condition_flag = False
    imp_flag = False
    peak_flag = False
    result_flag = False
    for col_name in table[0]:
        if condition_match(col_name):
            condition_flag = True
        elif imp_match(col_name):
            imp_flag = True
        elif peak_match(col_name):
            peak_flag = True
        elif result_match(col_name):
            result_flag = True

    return condition_flag and imp_flag and peak_flag and result_flag


# Above here are some utility functions that are specific for this document type
# TODO: perhaps move the above functions to specific util class


def extract_text(path):
    text = extract_raw_text(path)

    text_data = parse_pdf3_text(text)

    if "Model" not in text_data:
        model_match = re.search(r"(CYCLING|SNOW)[\\/][\w\s+°]+", path)
        if model_match:
            model = re.sub(r"(CYCLING|SNOW)[\\/]", "", model_match[0])

            if 0 in text_data:
                i = 0
                while i in text_data:
                    text_data[i]["Model"] = model
                    i += 1
            else:
                text_data["Model"] = model

    helmet_type = re.search(r"(CYCLING|SNOW)", path)
    if helmet_type:
        helmet_type = helmet_type[0]
        text_data["Helmet Type"] = helmet_type
    else:
        i = 0
        while i in text_data:
            text_data[i]["Helmet Type"] = get_helmet_type(text_data[i]["Model"])
            i += 1

    stage_of_testing = re.search(r"(Development|BatchTesting|Certificates)", path)
    if stage_of_testing:
        text_data["Stage of Testing"] = stage_of_testing[0]

    return text_data


def table_indices(tables):
    index = 0
    indices = []
    for table in tables:
        if is_table(table):
            indices.append(index)
        index += 1
    return indices


def extract_table_data(path):
    """Returns a list of tables (the tables are in themselves lists of lists)"""
    try:
        tables = extract_tables(path)
    except IndexError:
        print("No matching table in document!")
        return None

    return [tables[i] for i in table_indices(tables)]


def extract_pdf3(path):
    text_data = extract_text(path)
    table_data = extract_table_data(path)

    if table_data and text_data:
        return {"text_data": text_data, "table_data": table_data}

    return None
