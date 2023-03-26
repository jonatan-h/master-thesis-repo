import xlrd
from re import search, sub


def active_sheet(workbook):
    active_sheet = 0
    for sheet in workbook.sheets():
        if sheet.sheet_selected:
            return active_sheet
        active_sheet += 1

    return 0


def extract_e2(path):
    wb = xlrd.open_workbook(path, formatting_info=True)

    helmet_type = search(r"(CYCLING|SNOW)", path)[0]

    stage_of_testing = search(r"(Development|BatchTesting|Certificates)", path)[0]
    # create copy with separated values of merged rows and columns

    model = ""
    model_match = search(r"(CYCLING|SNOW)[\\/][\w\s+°]+", path)
    if model_match:
        model = sub(r"(CYCLING|SNOW)[\\/]", "", model_match[0])
    # create copy with separated values of merged rows and columns
    data = {"workbook": [],
            "active_sheet": active_sheet(wb),
            "helmet_type": helmet_type,
            "model": model,
            "stage_of_testing": stage_of_testing
            }
    num_rows = 0
    for sheet in wb.sheets():

        sheet_copy = [["" for c in range(sheet.ncols)] for r in range(sheet.nrows)]
        for row_index in range(sheet.nrows):
            for col_index in range(sheet.ncols):
                # print("row index: {0}".format(row_index))
                # print("col index: {0}".format(col_index))
                sheet_copy[row_index][col_index] = sheet.cell_value(rowx=row_index, colx=col_index)

        # copy values of merged rows and columns to all included rows and columns
        for merged_cells in sheet.merged_cells:
            rs, re, cs, ce = merged_cells
            # print("rs: {}, re: {}, cs: {}, ce: {}".format(rs, re, cs, ce))
            for row_index in range(rs, re):
                for col_index in range(cs, ce):
                    # print("merged cell value: {}".format(sheet.cell_value(rowx=rs, colx=cs)))
                    sheet_copy[row_index][col_index] = sheet.cell_value(rowx=rs, colx=cs)
        data["workbook"].append(sheet_copy)

    return data
