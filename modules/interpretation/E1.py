import re
import sys

import Dictionaries
from util import make_uniform, translate_test_condition, standardize_certification, translate_impact_location

helmet_type = ""
model = ""
stage_of_testing = ""
test_type = ""


def set_values(sheet, row):
    global model
    global stage_of_testing
    global test_type

    data = {}
    for i in range(len(row)):
        col_name = sheet[0][i]
        if not col_name:
            continue

        if not row[1]:
            return None

        key = ""
        value = ""

        if re.search(r"ID C(ODE|ode)", str(col_name)):
            continue

        elif re.search(r"((EPP|EPS) S(hell|HELL)|Density|DENSITY)", str(col_name)):
            value = str(row[i])
            if re.search(r"\d+[Pp]", value):
                key = "epp_density"
            else:
                key = "eps_density"
                if re.match(r"\d+$", value):
                    value = int(value)
            if key in data:
                value = "{}+{}".format(data[key], value)
            # value = "{} {}".format(row[i], Dictionaries.epp_to_eps(str(row[i])))

        elif re.search(r"(HEAD|Head)\s*(FORM|Form)", str(col_name)):
            key = "headform"
            value = row[i]

        elif re.search(r"(Test|TEST)\s+(COND|Cond)(ITION|ition)?", str(col_name)):
            key = "test_condition"
            value = translate_test_condition(str(row[i]))

        # TODO: maybe rework this once impact locations are made more uniform
        elif re.search(r"(Imp\.\s+Location|IMPACT\s+LOCATION[\s\S]+2|IMPACT\s+LOCATION)", str(col_name)):
            key = "impact_location"
            value = str(row[i]).lstrip().rstrip()
            if not value:
                return None
            # print("impact location: {}".format(row[i]))
            value = translate_impact_location(value, model, stage_of_testing, test_type)

        elif re.search(r"(Impact\s+Peak\s+Acc|PEAK\s+LINEAR\s+ACCELERATION)", str(col_name)):
            # key = str(key).split("/")[0]
            key = "peak"
            value = str(row[i])
            if re.match(r"\d+(.\d+)?$", value):
                value = float(value)
            else:
                return None

        elif re.search(r"(CRITERIA|Criteria)", str(col_name)):
            key = "criteria"
            value = row[i]

        elif re.search(r"(=Impact|IMPACT\s+RETENTION)", str(col_name)):
            # we don't care about retention tests
            if re.search("Retention|RETENTION", str(row[i])):
                return None
            continue

        elif re.search(r"(SAFETY\s+FACTOR|Safety\s+Factor)", str(col_name)):
            key = "safety_factor"
            try:
                value = round(float(row[i]), 2)
            except (ValueError, TypeError):
                return None

        elif re.search(r"(Date|DATE)", str(col_name)):
            key = "date"
            value = str(row[i])

        elif re.search(r"Anvil|ANVIL\s+TYPE", str(col_name)):
            key = "anvil"
            value = make_uniform(row[i])

        elif re.search(r"(TEST\s+NAME|Test\s+Type)", str(col_name)):
            key = "test_type"
            value = standardize_certification(row[i], helmet_type)

            if not test_type:
                test_type = value

        elif re.search(r"(RESULT|Result)", str(col_name)):
            key = "result"
            value = str(row[i])

        elif re.search(r"(SIZE|Size)", str(col_name)):
            key = "size"

            # TODO: check if this works as intended
            size = re.sub(r"\s+", "", str(row[i]))
            if re.search(r"\d+-\d+cm", size):
                value = Dictionaries.helmet_size_translation[size]
            else:
                value = size

        if value and key:
            data[key] = value
    return data


def interpret_e1(data):
    output = []

    global helmet_type
    helmet_type = data["helmet_type"]
    global model
    model = data["model"]
    global stage_of_testing
    stage_of_testing = data["stage_of_testing"]

    for sheet in data["workbook"]:
        for row in sheet[1:]:
            # print("Column A: {}".format(row[0]))

            entry = set_values(sheet, row)
            if entry:
                entry["helmet_type"] = helmet_type
                entry["model"] = model
                entry["stage_of_testing"] = stage_of_testing
                output.append(entry)
            # print("\n")
    return output
