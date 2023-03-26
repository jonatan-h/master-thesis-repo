# from modules.extraction.PDFMiner import extract_raw_text
from modules.extraction.PDFPlumber import extract_raw_text, extract_tables
import tabula
import pandas
from modules.extraction.TextParser import parse_pdf4_text
import re


def extract_text(path):
    text = extract_raw_text(path)

    text_data = parse_pdf4_text(text)

    model_match = re.search(r"(CYCLING|SNOW)[\\/][\w\s+°]+", path)
    if model_match:
        model = re.sub(r"(CYCLING|SNOW)[\\/]", "", model_match[0])
        text_data["Model"] = model

    helmet_type = re.search(r"(CYCLING|SNOW)", path)
    if helmet_type:
        text_data["Helmet Type"] = helmet_type[0]

    stage_of_testing = re.search(r"(Development|BatchTesting|Certificates)", path)
    if stage_of_testing:
        text_data["Stage of Testing"] = stage_of_testing[0]

    return text_data


def extract_table_data(path):
    table = extract_tables(path)

    return table


def extract_pdf4(path):
    text_data = extract_text(path)
    table_data = extract_table_data(path)

    return {"text_data": text_data, "table_data": table_data}
