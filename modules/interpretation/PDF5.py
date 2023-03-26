import Dictionaries
from util import calculate_safety_factor, determine_result, make_uniform, translate_test_condition, \
    standardize_certification, translate_impact_location
import re

model = ""
stage_of_testing = ""
test_type = ""


def verify_data_types(data):
    # TODO: perhaps add more attributes to type check
    return "test_type" in data and type(data["test_type"]) is str \
           and "criteria" in data and type(data["criteria"]) is int \
           and "size" in data and type(data["size"]) is str


def interpret_text(text_data):
    try:
        data = {"test_type": standardize_certification(re.match(r"[\s\w/]+", text_data["TEST SPECIFICATION"])[0], text_data["Helmet Type"]),
                "criteria": int(text_data["Criteria"]),
                "helmet_type": text_data["Helmet Type"],
                "stage_of_testing": text_data["Stage of Testing"]
                }
        global stage_of_testing
        stage_of_testing = text_data["Stage of Testing"]

        global test_type
        test_type = standardize_certification(re.match(r"[\s\w/]+", text_data["TEST SPECIFICATION"])[0], text_data["Helmet Type"])

        size_match = re.search(r"(\d+\s*-\s*\d+\s+\w+)", text_data["Helmet Size"])
        if size_match:
            size = re.sub(r"\s+", "", size_match[0])
            data["size"] = Dictionaries.helmet_size_translation[size]

        # TODO: perhaps better to get this from file path as well as with PDF1
        model_match = re.search(r"[\w\s]+$", text_data["Helmet Model"])
        if model_match:
            global model
            model = re.sub(r"(bicycle|snow)\s+helmet(s)?", "", model_match[0])
            model = re.sub(r"POC\s+", "", model)
            if model:
                model = model.lstrip().rstrip()

            data["model"] = model

    except KeyError as e:
        print("PDF5: Missing key from text data "+str(e))
        return None
    return data


def interpret_table(table):
    global model
    global stage_of_testing
    global  test_type

    output = []
    for i in range(1, len(table)):
        row = {}
        for j in range(0, len(table[i])):
            if re.search(r"HELMET\s+INFORMATION", str(table[0][j])):
                value = str(table[i][j])
                if not value:
                    temp_i = i
                    while not value or temp_i > 1:
                        value = str(table[temp_i-1])
                        temp_i -= 1

                row["test_condition"] = translate_test_condition(value)

            elif re.search(r"(Impact\s+[Ss]ite|IMPACT\s+SITE)", str(table[0][j])):
                value = str(table[i][j]).lstrip().rstrip()
                if not value:
                    row = {}
                    break
                row["impact_location"] = translate_impact_location(value, model, stage_of_testing, test_type)
            elif re.search("(Peak|PEAK)", str(table[0][j])):
                row["peak"] = float(table[i][j])
            elif re.search("(Assessment|ASSESSMENT)", str(table[0][j])):
                row["result"] = str(table[i][j]).upper()

        output.append(row)
    return output


def interpret_pdf5(data):
    text_data = interpret_text(data["text_data"])
    output = interpret_table(data["table_data"])

    if not text_data or not output:
        return None

    aux = []
    for row in output:
        # merge text data into rest of output data (for all entries)
        merged_row = row | text_data
        if not verify_data_types(merged_row):
            #TODO: look into issue where some reports are not extracted properly with the current tool
            print("PDF5: data type verification failed!")
            return None
        safety_factor = calculate_safety_factor(merged_row["peak"], merged_row["criteria"])
        merged_row["safety_factor"] = safety_factor

        result = determine_result(safety_factor)
        merged_row["result"] = result

        aux.append(merged_row)
    output = aux

    return output
