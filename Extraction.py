from modules.extraction.E1 import extract_e1
from modules.extraction.E2 import extract_e2
from modules.extraction.PDF1 import extract_pdf1
from modules.extraction.PDF2 import extract_pdf2
from modules.extraction.PDF4 import extract_pdf4
from modules.extraction.PDF3 import extract_pdf3
from modules.extraction.PDF5 import extract_pdf5


def extract(path, report_type):
    data = None
    if report_type == "E1":
        data = extract_e1(path)
    elif report_type == "E2":
        data = extract_e2(path)
    elif report_type == "PDF1":
        data = extract_pdf1(path)
    elif report_type == "PDF2":
        data = extract_pdf2(path)
    elif report_type == "PDF3":
        data = extract_pdf3(path)
    elif report_type == "PDF4":
        data = extract_pdf4(path)
    elif report_type == "PDF5":
        data = extract_pdf5(path)
    else:
        print("Report type not supported")
        return None

    return data

