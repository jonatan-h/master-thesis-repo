import Dictionaries
import re

from util import calculate_safety_factor, make_uniform, translate_test_condition, standardize_certification, \
    translate_impact_location
import queue

stage_of_testing = ""
test_type = ""

num_rows = 0


def verify_data_types(data):
    # TODO: perhaps add more attributes to type check
    return type(data["test_type"]) is str \
           and type(data["criteria"]) is int \
           and type(data["size"]) is str


def interpret_text(text_data, model_queue):
    try:
        data = {"test_condition": translate_test_condition(str(text_data["Conditioning"])),
                "headform": re.match(r"\w+", text_data["Headform Size"])[0],
                "size": re.match("[A-Z]", text_data["Size"])[0],
                "model": text_data["Model"],
                "test_type": standardize_certification(text_data["Standard Request"], text_data["Helmet Type"]),
                "helmet_type": text_data["Helmet Type"],
                "stage_of_testing": text_data["Stage of Testing"],
                }
        model_queue.put(text_data["Model"])
        global stage_of_testing
        stage_of_testing = text_data["Stage of Testing"]

        global test_type
        test_type = standardize_certification(text_data["Standard Request"], text_data["Helmet Type"])

        criteria = text_data["Maximum Peak G's authorized"] if "Maximum Peak G's authorized" in text_data \
            else text_data["Maximum Peak G's authorize"]
        number_match = re.search(r"\d+", criteria)
        if number_match:
            data["criteria"] = int(number_match[0])

        # if eps density is given in Batch number field, take it from there
        density_match = re.search(r"\d+", text_data["Batch Number"])
        if density_match:
            multiple_densities_match = re.search(r"\d+([Pp]|g/[Ll])?\s*[+/&]\s*\d+([Pp]|g/[Ll])", text_data["Batch Number"])
            if multiple_densities_match:
                density = multiple_densities_match[0]
                if re.search(r"\d+P", density):
                    data["epp_density"] = density
                else:
                    data["eps_density"] = density
            else:
                epp_match = re.search(r"\d+[Pp]", text_data["Batch Number"])
                if epp_match:
                    data["epp_density"] = epp_match[0]
                else:
                    eps_match = re.search(r"\d+", text_data["Batch Number"])
                    if eps_match:
                        data["eps_density"] = int(eps_match[0])
        # otherwise, take it from the identification code (if present)
        else:
            eps_match = re.search(r"\d+[SsMmLl]", text_data["Identification Code"])[0]
            if eps_match:
                data["eps_density"] = int(re.search(r"\d+", eps_match)[0])

    except KeyError as e:
        print("PDF1: Missing key from text data "+str(e))
        return None
    return data


# def table_head(table):
#     row_index = 0
#     for row in table:
#         for cell in row:
#             if re.search(r"(Peak|Anvil|Position|PASS)", str(cell)):
#                 return row_index
#         row_index += 1
#     return None


def interpret_table(table, model):
    global stage_of_testing
    global test_type

    table_head_index = 0 if str(table[0][0]) == "Impact" else 1

    output = []
    for i in range(table_head_index+3, len(table)):
        row = {}
        for j in range(0, len(table[i])):
            # print("table[{}][{}]: {}".format(i, j, table[i][j]))
            if not table[i][j]:
                continue
            col_name = str(table[table_head_index][j])
            if re.search("Peak", col_name):
                row["peak"] = float(table[i][j])
            elif re.search("Anvil", col_name):
                row["anvil"] = make_uniform(table[i][j])
            elif re.search("Position", col_name):
                impact_location = str(table[i][j]).lstrip().rstrip()
                if not impact_location:
                    row = {}
                    break
                row["impact_location"] = translate_impact_location(impact_location, model, stage_of_testing, test_type)
            elif re.search("PASS", col_name):
                row["result"] = str(table[i][j]).upper()

        # print("peak: {}, anvil: {}, impact_location: {}, result: {}".format("peak" in row, "anvil" in row, "impact_location" in row, "result" in row))
        if "peak" in row and "anvil" in row and "impact_location" in row and "result" in row:
            output.append(row)

    global num_rows
    num_rows += len(output)
    return output


def interpret_pdf1(data):
    text_data = data["text_data"]

    model_queue = queue.Queue()
    interpreted_text_data = []
    i = 0
    while i in text_data:
        interpreted_text_data.append(interpret_text(text_data[i], model_queue))
        i += 1

    table_data = data["table_data"]

    table_out = []
    for table in table_data:
        model = model_queue.get()
        table_out.append(interpret_table(table, model))
    global num_rows
    print("num rows (PDF1): {}".format(num_rows))


    if not interpreted_text_data or not table_out:
        return None

    aux = []
    table_index = 0
    for table in table_out:
        for row in table:
            # merge text data into rest of output data (for all entries)
            merged_row = row | interpreted_text_data[table_index]
            if not verify_data_types(merged_row):
                print("PDF1: data type verification failed!")
                return None
            safety_factor = calculate_safety_factor(merged_row["peak"], merged_row["criteria"])
            merged_row["safety_factor"] = safety_factor

            # Result is already provided and so it does not need to be computed again

            aux.append(merged_row)
        table_index += 1
    output = aux

    return output
