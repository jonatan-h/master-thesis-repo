import pdfplumber


def extract_raw_text(path):
    with pdfplumber.open(path) as pdf:
        pages = []
        for page in pdf.pages:
            # print("\nPAGE NUMBER {}\n".format(page.page_number))
            page_text = page.extract_text()
            # print(page_text)
            pages.append(page_text)
    return pages


def extract_tables(path):
    """Extracts all tables on each page and appends them to a list of tables (as a list of lists of lists)"""
    with pdfplumber.open(path) as pdf:
        tables = []
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    return tables
