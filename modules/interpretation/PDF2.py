import Dictionaries
from util import calculate_safety_factor, make_uniform, translate_test_condition, standardize_certification, \
    translate_impact_location
import re

model = ""
stage_of_testing = ""
test_type = ""

num_rows = 0


# TODO: perhaps move type check to separate file rather than having one for each
def verify_data_types(data):
    # TODO: perhaps add more attributes to type check
    return type(data["test_type"]) is str \
           and type(data["criteria"]) is int \
           and type(data["size"]) is str


def interpret_fixed_text_data(text_data):
    try:
        data = {
                "model": str(text_data["Model"]),
                "criteria": int(text_data["Criteria"]),
                "headform": text_data["Headform"],
                "test_type": standardize_certification(text_data["Standard"], text_data["Helmet Type"]),
                "helmet_type": text_data["Helmet Type"],
                "stage_of_testing": text_data["Stage of Testing"]
                }
        if "EPP Density" in text_data and re.search(r"\d+[Pp]", text_data["EPP Density"]):
            data["epp_density"] = str(text_data["EPP Density"])
        elif "EPS Density" in text_data and re.search(r"$\d+^", str(text_data["EPS Density"])):
            data["eps_density"] = int(text_data["EPS Density"])

        if "Anvil" in text_data:
            data["anvil"] = str(text_data["Anvil"])

        if re.search(r"(\d+-\d+cm|Small|Medium|Large)", text_data["Size"]):
            value = Dictionaries.helmet_size_translation[text_data["Size"]]
            data["size"] = value
        else:
            data["size"] = re.search(r"[A-Z-]+", str(text_data["Size"]))[0]

        global stage_of_testing
        stage_of_testing = text_data["Stage of Testing"]

        global test_type
        test_type = standardize_certification(text_data["Standard"], text_data["Helmet Type"])

    except KeyError as e:
        print("PDF2: Missing key from fixed text data "+str(e))
        return None
    return data


def interpret_variable_text_data(text_data):
    try:
        data = {}
        if "Size" in text_data:
            value = str(text_data["Size"])
            data["size"] = Dictionaries.helmet_size_translation[value]
        if "Headform" in text_data:
            data["headform"] = text_data["Headform"]
    except KeyError as e:
        print("PDF2: Missing key from variable text data")
    return data


def interpret_table(table):
    global stage_of_testing
    global test_type

    output = []
    for i in range(1, len(table)):
        row = {}
        for j in range(0, len(table[i])):
            if re.search(r"(Sample\s+No.|Environment\s+Impact)", str(table[0][j])):
                value = table[i][j]
                if not value:
                    temp_i = i
                    while not value and temp_i > 1:
                        value = table[temp_i-1][j]
                        temp_i -= 1

                letter_match = re.search(r"[A-Za-z]+", str(value))
                if letter_match:
                    row["test_condition"] = translate_test_condition(letter_match[0])
            elif re.search(r"(Test\s+)?[Aa]nvil", str(table[0][j])):
                value = table[i][j]
                if value:
                    value = str(value)
                    row["anvil"] = make_uniform(value)
                # If merged column, copy from cell above
                else:
                    temp_i = i
                    while not value and temp_i > 1:
                        value = table[temp_i-1][j]
                        temp_i -= 1
                    value = str(value)
                    row["anvil"] = make_uniform(value)
            elif re.search(r"Location\s+Impact", str(table[0][j])):
                value = str(table[i][j]).lstrip().rstrip()
                if not value:
                    row = {}
                    break
                row["impact_location"] = translate_impact_location(value, model, stage_of_testing, test_type)
            elif re.search("Peak", str(table[0][j])):
                value = re.match(r"\d+(\.\d+)?", table[i][j])
                if value:
                    row["peak"] = float(value[0])
                else:
                    row = {}
                    break
            elif re.search("Compliant", str(table[0][j])):
                row["result"] = table[i][j].upper()

        output.append(row)

    global num_rows
    num_rows += len(output)
    return output


def interpret_pdf2(data):
    text_data = data["text_data"]
    fixed_text_data = interpret_fixed_text_data(text_data)
    variable_text_data = []

    i = 0
    while i in text_data:
        variable_text_data.append(interpret_variable_text_data(text_data[i]))
        i += 1

    table_data = data["table_data"]
    table_out = []

    for table in table_data:
        table_out.append(interpret_table(table))
    # output = interpret_table(data["table_data"])
    global num_rows
    print("num rows (PDF2): {}".format(num_rows))

    if not fixed_text_data or not table_out:
        return None

    aux = []
    table_index = 0
    for table in table_out:
        for row in table:
            # merge text data into rest of output data (for all entries)
            merged_row = row | fixed_text_data

            if len(variable_text_data) > table_index and variable_text_data[table_index]:
                merged_row = merged_row | variable_text_data[table_index]

            if not verify_data_types(merged_row):
                #TODO: look into issue where some reports are not extracted properly with the current tool
                print("PDF2: data type verification failed!")
                return None
            safety_factor = calculate_safety_factor(merged_row["peak"], merged_row["criteria"])
            merged_row["safety_factor"] = safety_factor

            # Result already included in report

            aux.append(merged_row)
        table_index += 1
    output = aux

    print(output)

    return output
