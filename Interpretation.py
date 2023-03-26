from modules.interpretation.E1 import interpret_e1
from modules.interpretation.E2 import interpret_e2
from modules.interpretation.PDF1 import interpret_pdf1
from modules.interpretation.PDF2 import interpret_pdf2
from modules.interpretation.PDF3 import interpret_pdf3
from modules.interpretation.PDF4 import interpret_pdf4
from modules.interpretation.PDF5 import interpret_pdf5


def interpret(data, report_type):
    output = ""
    if report_type == "E1":
        output = interpret_e1(data)
        # print("output data: ")
        # for row in output:
        #     print(row)
    elif report_type == "E2":
        output = interpret_e2(data)
        # print("output data: ")
        # for row in output:
        #     print(row)
    elif report_type == "PDF1":
        output = interpret_pdf1(data)
    elif report_type == "PDF2":
        output = interpret_pdf2(data)
    elif report_type == "PDF3":
        output = interpret_pdf3(data)
    elif report_type == "PDF4":
        output = interpret_pdf4(data)
        # print("output data: ")
        # for row in output:
        #     print(row)
    elif report_type == "PDF5":
        output = interpret_pdf5(data)
    else:
        output = None

    return output


