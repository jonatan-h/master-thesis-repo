from modules.extraction.PDFPlumber import extract_raw_text, extract_tables
from modules.extraction.TextParser import parse_pdf2_text
import re
from util import get_helmet_type

headform = ""


def find_headform(tables):
    for table in tables:
        for i in range(0, len(table[0])):
            if str(table[0][i]) == "Impact headform":
                return str(table[1][i])
    return None


def extract_text(path):
    text = extract_raw_text(path)

    text_data = parse_pdf2_text(text)

    if "Headform" in text_data:
        global headform
        headform = text_data["Headform"]

    helmet_type = re.search(r"(CYCLING|SNOW)", path)
    if helmet_type:
        text_data["Helmet Type"] = helmet_type[0]
    else:
        try:
            text_data["Helmet Type"] = get_helmet_type(text_data["Model"])
        except KeyError:
            print("Model missing, cannot ")

    stage_of_testing = re.search(r"(Development|BatchTesting|Certificates)", path)
    if stage_of_testing:
        text_data["Stage of Testing"] = stage_of_testing[0]

    return text_data


def table_indices(tables):
    index = 0
    indices = []
    for table in tables:
        if (len(table[0]) > 1 and re.match(r"(Test\s+)?[Aa]nvil", str(table[0][1]))) \
                or len(table[0]) > 3 and re.match(r"Peak", str(table[0][3])) \
                or (len(table[0]) > 2 and re.match(r"(Test\s+)?[Aa]nvil", str(table[0][2]))):
            indices.append(index)
        index += 1
    return indices


def extract_table_data(path):
    try:
        tables = extract_tables(path)
        # for table in tables:
        #     print("{}\n".format(table))

        global headform
        if not headform:
            headform = find_headform(tables)
    except IndexError:
        print("No matching table in document!")
        return None

    return [tables[i] for i in table_indices(tables)]


def extract_pdf2(path):
    text_data = extract_text(path)
    table_data = extract_table_data(path)

    if "Headform" not in text_data:
        global headform
        text_data["Headform"] = headform

    if table_data and text_data:
        return {"text_data": text_data, "table_data": table_data}

    return None
