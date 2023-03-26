import re

import DBConnector
import Extraction
import Interpretation
from modules.identification.Modules import report_type
from modules.export.DB import store
import os

from modules.extraction.PDF4 import extract_text, extract_table_data

# When processing all files
# root_folder = "./reports"

# When processing just the Development files
root_folder = './reports/Helmet_Data/Reports'

if __name__ == '__main__':

    # path = "./documents/excel1.xlsx"
    # path = "./documents/excel2.xls"
    # path = "./documents/pdf1.pdf"
    # pdfminer_test = "./documents/pdf2.pdf"
    # pdfminer_test = "./documents/pdf4.pdf"
    # text = extract_text(pdfminer_test)
    # tables = extract_table_data(pdfminer_test)
    # path = "./documents/pdf4.pdf"
    # path = "./reports/Helmet_Data/Reports/01_Development/01_CYCLING/Axion/POC AXION RACE MIPS AXION  S inhouse test record20210611.xls"
    # path = "./reports/Helmet_Data/Reports/01_Development/01_CYCLING/Axion MIPS/Test summary of Axion race Mips 210202.xls"
    # path = "./reports/Helmet_Data/Reports/01_Development/01_CYCLING/Myelin/POC-5 -M(EN1078)(01 COLD) -POC210521.pdf"

    counter = 1

    connection = DBConnector.create_connection("localhost", "root", "_YfN_[U6Tm4[_#JC")
    # DBConnector.show_databases(connection)  # only for showcasing purposes
    DBConnector.use(connection, "test", False)
    # DBConnector.show_tables(connection)  # only for showcasing purposes

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            # if counter > 385:
            #     break

            # TODO: maybe only open the file once, and close after finished
            write_file_location = "C:/Users/johol/Documents/POC_write_cache.txt"
            # with open(os.path.join(root, file), "r") as f:
            if file.endswith("xls") or file.endswith("xlsx") or file.endswith("pdf"):
                path = os.path.join(root, file)
                path = re.sub(r"\\", "/", path)
                print("path: " + path)

                write_cache = open(write_file_location, "r")
                write_cache_content = write_cache.read()
                if path in str(write_cache_content):
                    print("File has already been processed.\n")
                    continue
                write_cache.close()

                r_type = report_type(path)
                print("Report Type: {}".format(r_type))
                if r_type == -1:
                    continue
                data = Extraction.extract(path, r_type)
                # print(data)
                # if no extraction performed, abort
                if not data:
                    print("Extraction failed!")
                    counter += 1
                    continue
                output = Interpretation.interpret(data, r_type)

                if not output:
                    print("Interpretation failed!")
                    continue

                outfile = "C:/Users/johol/Documents/POC_report_output/outfile{}.txt".format(hash(path))
                f = open(outfile, "w", encoding="utf-8")
                write_data = str(file) + "\n\n"

                for row in output:
                    store(connection, row)
                    # for key in row:
                    #     entry = key + " -> " + str(row[key])
                    #     if not key == list(row.keys())[-1]:
                    #         write_data = write_data + entry + ", "
                    #     else:
                    #         write_data = write_data + entry + "\n"
                # print(write_data + "\n\n")
                f.write(write_data)
                f.close()
                print("WRITE OK: {}\n".format(outfile))
                write_cache = open(write_file_location, "a")
                write_cache.write(path+"\n")
                write_cache.close()

                counter += 1
    # DBConnector.select_all(connection, "test_suite", True)
