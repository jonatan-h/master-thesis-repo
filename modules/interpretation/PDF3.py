import Dictionaries
from util import calculate_safety_factor, determine_result, make_uniform, translate_test_condition, \
    standardize_certification, translate_impact_location
import re
import queue

stage_of_testing = ""
test_type = ""
standard = ""

num_rows = 0


# TODO: perhaps move type check to separate file rather than having one for each
def verify_data_types(data):
    # TODO: perhaps add more attributes to type check
    if "test_type" not in data or "criteria" not in data or "size" not in data:
        return False
    return type(data["test_type"]) is str \
        and type(data["criteria"]) is int \
        and type(data["size"]) is str


def interpret_fixed_text(text_data):
    try:
        data = {"criteria": int(text_data["Criteria"]),
                "stage_of_testing": text_data["Stage of Testing"],
                }
        if "Model" in text_data:
            data["model"] = text_data["Model"]
        if "Anvil" in text_data:
            data["anvil"] = text_data["Anvil"]

        if "Helmet Type" in text_data:
            data["helmet_type"] = text_data["Helmet Type"]
            data["test_type"] = standardize_certification(text_data["Standard"], text_data["Helmet Type"])
        else:
            global standard
            standard = text_data["Standard"]

        global stage_of_testing
        stage_of_testing = text_data["Stage of Testing"]

        if "Liner" in text_data:
            if text_data["Liner"] == "EPS":
                data["eps_density"] = int(re.search(r"\d+", text_data["Liner Density"])[0])
            else:
                data["epp_density"] = int(re.search(r"\d+", text_data["Liner Density"])[0])
    except KeyError as e:
        print("PDF3: Missing key from fixed text data "+str(e))
        return None
    return data


def interpret_variable_text(text_data, model_queue):
    try:
        data = {"model": text_data["Model"],
                "size": Dictionaries.helmet_size_translation[re.sub(r"\s+", "", text_data["Size"])],
                "headform": text_data["Headform"],
                }
        if "Model" in text_data:
            data["model"] = text_data["Model"]

        if "Helmet Type" in text_data:
            global standard
            data["helmet_type"] = text_data["Helmet Type"]
            data["test_type"] = standardize_certification(standard, text_data["Helmet Type"])

        model_queue.put(text_data["Model"])
    except KeyError as e:
        print("PDF3: Missing key from variable text data "+str(e))
        return None
    return data


def interpret_table(table, model):
    global stage_of_testing
    global test_type

    output = []
    for i in range(1, len(table)):
        row = {}
        for j in range(0, len(table[i])):
            if re.search(r"Condition", str(table[0][j])):
                value = table[i][j]
                if not value:
                    temp_i = i
                    while not value and temp_i > 1:
                        value = table[temp_i-1][j]
                        temp_i -= 1

                row["test_condition"] = translate_test_condition(value)

            elif re.search(r"(Test\s+)?[Aa]nvil", str(table[0][j])):
                if table[i][j]:
                    row["anvil"] = make_uniform(table[i][j])
                # If merged column, copy from cell above
                elif table[i-1][j]:
                    row["anvil"] = table[i-1][j]
            elif re.search(r"(Impact|Test)\s+[Ss]ite", str(table[0][j])):
                value = str(table[i][j]).lstrip().rstrip()
                if not value:
                    row = {}
                    break
                row["impact_location"] = translate_impact_location(value, model, stage_of_testing, test_type)
            # TODO: attribute name in row might be subject to change to "speed"
            elif re.search("Velocity", str(table[0][j])):
                row["velocity"] = float(table[i][j])
            elif re.search("Peak", str(table[0][j])):
                row["peak"] = float(table[i][j])
            elif re.search("Result", str(table[0][j])):
                row["result"] = str(table[i][j]).upper()
            elif re.search("Size", str(table[0][j])):
                size = table[i][j]
                if not size:
                    temp_i = i
                    while not size and temp_i > 1:
                        size = table[temp_i-1][j]
                        temp_i -= 1
                try:
                    row["size"] = Dictionaries.helmet_size_translation[str(size)]
                except KeyError:
                    print("Size not found!")
            elif re.search("Headform", str(table[0][j])):
                headform = table[i][j]
                if not headform:
                    temp_i = i
                    while not headform and temp_i > 1:
                        headform = table[temp_i-1][j]
                        temp_i -= 1
                row["headform"] = str(headform)

        output.append(row)
    global num_rows
    num_rows += len(output)
    return output


def interpret_pdf3(data):
    text_data = data["text_data"]
    fixed_text_data = interpret_fixed_text(text_data)
    variable_text_data = []

    model_queue = queue.Queue()
    i = 0
    while i in text_data:
        variable_text_data.append(interpret_variable_text(text_data[i], model_queue))
        i += 1
    table_data = data["table_data"]
    table_out = []
    for table in table_data:
        if not model_queue.empty():
            model = model_queue.get()
        else:
            model = None
        table_out.append(interpret_table(table, model))
    global num_rows
    print("num rows (PDF3): {}".format(num_rows))

    if not text_data or not table_out:
        return None

    aux = []
    table_index = 0
    for table in table_out:
        for row in table:
            # merge text data into rest of output data (for all entries)
            if fixed_text_data:
                merged_row = row | fixed_text_data
            else:
                return None
            if len(variable_text_data) > table_index and variable_text_data[table_index]:
                merged_row = merged_row | variable_text_data[table_index]
            if not verify_data_types(merged_row):
                print("PDF3: data type verification failed!")
                return None
            safety_factor = calculate_safety_factor(merged_row["peak"], merged_row["criteria"])
            merged_row["safety_factor"] = safety_factor

            # result = determine_result(safety_factor)
            # merged_row["result"] = result

            aux.append(merged_row)
        table_index += 1
    output = aux

    return output
