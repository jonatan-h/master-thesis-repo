from util import calculate_safety_factor, determine_result, make_uniform, translate_test_condition, \
    standardize_certification, translate_impact_location
import Dictionaries
import re

helmet_type = ""
stage_of_testing = ""
model = ""


def set_values(ws, row):
    row_entries = []

    global helmet_type
    global model
    global stage_of_testing

    test_type = re.findall(r"[0-9A-Za-z\s/\\-]+", ws[1][0])
    if test_type:
        test_type = standardize_certification(test_type[0], helmet_type)

    # TODO: translate variances in representation into uniform way (i.e. ASNZ rather than AS)
    common_set = {"test_type": test_type}
    # print(row)
    for common_col in range(6):
        if common_col == 0 or common_col == 2 or common_col == 3:
            continue
        # if common_col == 5:
        #     # if necessary, could also add epp translation
        #     value = row[common_col]
        #     common_set["eps_density"] = value
        #     continue

        # key = ws[2][common_col].lower()
        key = Dictionaries.e2_column_lookup[common_col]
        if key == "eps_density":
            # print(str(row[common_col]))
            match = re.match(r'\d+', str(row[common_col]))
            if match:
                value = int(match[0])
                # print("value: {}\n".format(value))
            else:
                continue
        elif key == "size":
            value = str(row[common_col])
            match = re.search(r"\d+[ -]\d+\s*[Cc][Mm]", value)
            if match:
                value = re.sub(r"\s+", "", match[0])
                value = Dictionaries.helmet_size_translation[value.lower()]

        else:
            value = str(row[common_col])
            match = re.search(r"[\w-]+", value)
            if match:
                value = match[0]
        # key = ws.cell_value(rowx=2, colx=common_col_index)  # key corresponding to value
        # value = ws.cell_value(rowx=row_index, colx=common_col_index)
        common_set[key] = value

    # for key in common_set:
    #     print(key, "->", common_set[key])

    if not common_set["size"] or not common_set["headform"]:
        return None

    for col in range(7, len(row)):
        entry = common_set
        if not row[col] or re.search(r"(P[Aa][sS]{2}|F[Aa][Ii][Ll])", str(row[col])):
            continue

        entry["helmet_type"] = helmet_type

        entry["stage_of_testing"] = stage_of_testing

        entry["model"] = model

        entry["anvil"] = make_uniform(ws[2][col])  # Anvil

        test_code_string = ws[4][col]
        if isinstance(test_code_string, str) and test_code_string and re.match(r"\s*[A-Za-z]\d+\s*$", test_code_string):
            impact_loc_code = re.search(r"\d+", test_code_string)
            if impact_loc_code:
                impact_loc_code = impact_loc_code[0]
                entry["impact_location"] = translate_impact_location(impact_loc_code, model, stage_of_testing, test_type)

        test_cond_value = str(ws[3][col]).upper()
        entry["test_condition"] = translate_test_condition(test_cond_value)

        value = row[col]
        if re.search(r"\d+[\s/]+\d+([\s/]+\d+)?", str(value)):  # if two values separated by whitespace or '/'
            values = re.split(r"[\s/]+", value)
            for v in values:
                try:
                    peak = float(v)
                except ValueError as e:
                    return None

                entry["peak"] = peak

                matches = re.split(r"=\D*", test_cond_value)
                if matches and len(matches) > 1:
                    criteria = re.sub("[^0-9]", "", matches[1])
                    entry["criteria"] = criteria

                    safety_factor = calculate_safety_factor(peak, criteria)
                    entry["safety_factor"] = safety_factor
                    entry["result"] = determine_result(safety_factor)

                row_entries.append(entry.copy())
        else:
            try:
                peak = float(value)
            except ValueError as e:
                print("ValueError: {}".format(e))
                return None

            entry["peak"] = peak

            matches = re.split(r"=\D*", test_cond_value)
            if matches and len(matches) > 1:
                criteria = re.sub("[^0-9]", "", matches[1])
                entry["criteria"] = criteria

                safety_factor = calculate_safety_factor(peak, criteria)
                entry["safety_factor"] = safety_factor
                entry["result"] = determine_result(safety_factor)

            row_entries.append(entry.copy())

    return row_entries


def interpret_e2(data):
    output = []

    global helmet_type
    helmet_type = data["helmet_type"]

    global stage_of_testing
    stage_of_testing = data["stage_of_testing"]

    global model
    model = data["model"]
    # for sheet in data:
    #     for row in sheet:
    #         print(row)
    active_sheet = data["active_sheet"]
    # print("active_sheet[4][0]: " + data["workbook"][active_sheet][4][0])
    # if not re.match(r"[0-9A-Za-z]", data["workbook"][active_sheet][4][0]):
    #     #TODO: add support for reports where the column names are in chinese
    #     print("E2: Currently no support for reports in chinese")
    #     return None

    for sheet in data["workbook"]:

        # skip roadmap sheet
        if len(sheet) < 2 or sheet[1][0] == "POC Test Roadmap":
            continue

        # print("Work sheet: {}\n".format(sheet.name))
        for r in range(5, len(sheet)):
            row_entries = set_values(sheet, sheet[r])
            if row_entries:
                output = output + row_entries

    print("num rows (E2): {}".format(len(output)))
    return output
