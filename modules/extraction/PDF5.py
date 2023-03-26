from modules.extraction.PDFPlumber import extract_raw_text, extract_tables
from modules.extraction.TextParser import parse_pdf5_text
import re


def is_valid(table):
    if not table or len(table) < 2:
        return False

    peak_flag = False
    condition_flag = False
    position_flag = False
    result_flag = False

    for i in range(0, 2):
        for col_name in table[i]:
            if re.search(r"(Peak|PEAK)", str(col_name)):
                peak_flag = True
            elif re.search("Condition", str(col_name)):
                condition_flag = True
            elif re.search(r"(Impact\s+[Ss]ite|IMPACT\s+SITE)", str(col_name)):
                position_flag = True
            elif re.search("(Assessment|ASSESSMENT)", str(col_name)):
                result_flag = True

    return peak_flag and condition_flag and position_flag and result_flag


def extract_text(path):
    text = extract_raw_text(path)

    text_data = parse_pdf5_text(text)

    helmet_type = re.search(r"(CYCLING|SNOW)", path)
    if helmet_type:
        text_data["Helmet Type"] = helmet_type[0]

    stage_of_testing = re.search(r"(Development|BatchTesting|Certificates)", path)
    if stage_of_testing:
        text_data["Stage of Testing"] = stage_of_testing[0]

    return text_data


def extract_table_data(path):
    """Returns a list of tables (the tables are in themselves lists of lists)"""
    try:
        tables = extract_tables(path)
    except IndexError:
        print("No matching table in document!")
        return None
    for table in tables:
        if is_valid(table):
            return table
    return None


def extract_pdf5(path):
    text_data = extract_text(path)
    table_data = extract_table_data(path)

    if table_data and text_data:
        return {"text_data": text_data, "table_data": table_data}

    return None
