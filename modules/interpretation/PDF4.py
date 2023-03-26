import re

import Dictionaries
from util import calculate_safety_factor, determine_result, make_uniform, translate_test_condition, \
    standardize_certification, translate_impact_location

model = ""
stage_of_testing = ""
test_type = ""

num_rows = 0


def verify_data_types(data):
    # TODO: perhaps add more attributes to type check
    return type(data["test_type"]) is str \
           and type(data["criteria"]) is int \
           and type(data["size"]) is str


def interpret_text(text_data):
    try:
        data = {"test_type": standardize_certification(text_data["Standard"], text_data["Helmet Type"]),
                "criteria": int(text_data["Max Peak [g]"]),
                "size": text_data["Helmet Size"].split("(")[0],
                # "eps_density": int(re.search(r"\d+", text_data["Density"])[0]),
                'model': text_data["Model"],
                "helmet_type": text_data["Helmet Type"],
                "stage_of_testing": text_data["Stage of Testing"]
                }

        density_match = re.search(r"\d+", text_data["Density"])
        if density_match:
            multiple_densities_match = re.search(r"\d+([Pp]|g/[Ll])?\s*[+/&]\s*\d+([Pp]|g/[Ll])", text_data["Density"])
            if multiple_densities_match:
                density = multiple_densities_match[0]
                if re.search(r"\d+P", density):
                    data["epp_density"] = density
                else:
                    data["eps_density"] = density
            else:
                epp_match = re.search(r"\d+[Pp]", text_data["Density"])
                if epp_match:
                    data["epp_density"] = epp_match[0]
                else:
                    eps_match = re.search(r"\d+", text_data["Density"])
                    if eps_match:
                        data["eps_density"] = int(eps_match[0])

        global stage_of_testing
        stage_of_testing = text_data["Stage of Testing"]

        global test_type
        test_type = standardize_certification(text_data["Standard"], text_data["Helmet Type"])

        global model
        model = data["model"]
    except KeyError as e:
        print("PDF4: Missing key from text data "+str(e))
        return None
    return data


def interpret_table(table):
    global model
    global stage_of_testing
    global test_type

    output = []
    length = len(table[0])
    if length > 1:
        for i in range(1, len(table[0])):
            if not table[0][i][0]:
                return output

            row = {}
            for j in range(0, len(table[0][0])):
                col_name = str(table[0][0][j])
                value = table[0][i][j]
                if re.search(r"Cond\.", col_name):
                    row["test_condition"] = translate_test_condition(str(value))
                elif re.search("Anvil", col_name):
                    row["anvil"] = make_uniform(value)
                elif re.search("Peak", col_name):
                    row["peak"] = float(value)
                elif re.search(r"Head\.\s*Size", col_name):
                    row["headform"] = value
                elif re.search(r"Impact\s+Point", col_name):
                    if not value:
                        row = {}
                        break
                    row["impact_location"] = translate_impact_location(value, model, stage_of_testing, test_type)
            if row:
                output.append(row)
    else:
        for i in range(0, len(table[1])):
            if not table[1][i][0]:
                return output

            row = {}
            for j in range(0, len(table[0][0])):
                col_name = str(table[0][0][j])
                value = table[1][i][j]
                if re.search(r"Cond\.", col_name):
                    row["test_condition"] = translate_test_condition(str(value))
                elif re.search("Anvil", col_name):
                    row["anvil"] = make_uniform(value)
                elif re.search("Peak", col_name):
                    row["peak"] = float(value)
                elif re.search(r"Head\.\s*Size", col_name):
                    row["headform"] = value
                elif re.search("Impact\s+Point", col_name):
                    row["impact_location"] = translate_impact_location(value, model, stage_of_testing, test_type)

            output.append(row)

    global num_rows
    num_rows += len(output)
    return output


def interpret_pdf4(data):
    text_data = interpret_text(data["text_data"])
    output = interpret_table(data["table_data"])

    global num_rows
    print("num rows (PDF4): {}".format(num_rows))

    if not text_data or not output:
        return None

    aux = []
    for row in output:
        # merge text data into rest of output data (for all entries)
        merged_row = row | text_data
        if not verify_data_types(merged_row):
            #TODO: look into issue where some reports are not extracted properly with the current tool
            print("PDF4: data type verification failed!")
            return None
        safety_factor = calculate_safety_factor(merged_row["peak"], merged_row["criteria"])
        merged_row["safety_factor"] = safety_factor

        result = determine_result(safety_factor)
        merged_row["result"] = result

        aux.append(merged_row)
    output = aux

    return output
