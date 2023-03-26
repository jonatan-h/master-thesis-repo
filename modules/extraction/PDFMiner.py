from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import tabula
import pandas


def extract_raw_text(filename):
    resource_manager = PDFResourceManager()
    return_string = StringIO()
    codec = 'utf-8'
    la_params = LAParams()
    device = TextConverter(resource_manager, return_string, codec=codec, laparams=la_params)
    fp = open(filename, 'rb')
    interpreter = PDFPageInterpreter(resource_manager, device)
    password = ""
    max_pages = 0
    caching = True
    page_nos = set()

    for page in PDFPage.get_pages(
            fp,
            page_nos,
            maxpages=max_pages,
            password=password,
            caching=caching,
            check_extractable=True):
        interpreter.process_page(page)
    text = return_string.getvalue()

    fp.close()
    device.close()
    return_string.close()

    # text = extract_text(filename)
    return text
