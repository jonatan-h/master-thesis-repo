from queue import Queue
import re
from util import is_anvil_type, make_uniform


def parse_text(text):
    data = {}
    q = Queue()
    for line in text.splitlines():
        if not line:
            continue
        key = None
        if line.endswith(':'):
            q.put(line)
        else:
            if not q.empty():
                key = re.sub("\s*\:", "", q.get())

        if key:
            data[key] = line

    return data


def line_check(line, report_type):
    # TODO: implement function to determine which lines to process
    match report_type:
        case "PDF1":
            # Size is used for "Headform Size" and "Size" attribute
            return re.search("(Conditioning|(Headform )?Size|Maximum Peak G's authorize(d)?|Batch Number|Standard Request|Identification Code)", line)

        case "PDF2":
            # TODO: find way to include EPP/EPS information
            return re.match(r"(Helmet Model|Item(/Model)? No\.|Model No\.|Size|Helmet [Ss]ize)", line)

        case "PDF3":
            return re.search(r"(Liner\s*(Density)?|Sample\s+Description)", line)
            # Model and Size are recorded by the "info row" which precedes every test (and might vary between these)
            # or re.search(r"(Style\s+/)\s*Item\s+No", line) or re.search(r"Size\s+:", line)

        case "PDF4":
            return re.search(r"Standard|Max Peak|Min Speed|Density|Helmet Size", line)

        case "PDF5":
            return re.search(r"(TEST SPECIFICATION|Helmet\s+(Model|Size)|Test headform\(s\) used)", line)

        case _:
            return None


def parse_pdf1_text(text):
    data = {}
    test_index = 0
    for page in text:
        params = {}
        for line in page.splitlines():
            if not line:
                continue
            if line.startswith("Impact Peak"):
                break
            key_match = line_check(line, "PDF1")
            if key_match:  # Check if line is among lines which have relevant information
                key_value = line.split(":")
                # key = re.sub('[0-9.]+', '', key_value[0]).lstrip().rstrip()
                key = key_match[0]

                # discard anything after space or brackets (such as unit or description)
                # TODO: pattern set can probably be simplified to [\w\.]
                match = re.match(r'[a-zA-Z0-9_/+&.\()\s-]+', key_value[1].lstrip().rstrip())
                if match:
                    params[key] = match[0]
            else:
                continue
        if re.search(r"Impact(\s*(Uni|Tri)-Axial)", page):
            data[test_index] = params
            test_index += 1
    return data


def parse_pdf2_text(text):
    data = {}
    test_index = 0
    for page in text:
        # anvil text can span multiple lines, hence checking whole page
        if "Anvil" not in data:
            anvil = is_anvil_type(page.lower())
            if anvil:
                anvil_match = re.search(r"using\s+a(\s*(See Appendix)|\s*Note(\s*1)?\))?\s+{}\s+anvil".format(anvil[0]), page)
                if anvil_match:
                    data["Anvil"] = make_uniform(anvil[0])

        for line in page.splitlines():
            if not line:
                continue
            if line.startswith("Photos for reference"):
                return data

            size_headform_match = re.search(r"(Size:\s*\d+-\d+\s*cm/)?Test [Hh]eadform:\s*\w+\s*$", line)
            if size_headform_match:
                size_match = re.search(r"\d+-\d+cm", size_headform_match[0])
                if size_match:
                    if test_index not in data:
                        data[test_index] = {
                            "Size": size_match[0]
                        }
                    else:
                        data[test_index]["Size"] = size_match[0]

                headform = size_headform_match[0].split(":")[-1].lstrip().rstrip()
                if test_index not in data:
                    data[test_index] = {
                        "Headform": headform
                    }
                else:
                    data[test_index]["Headform"] = headform

                test_index += 1

            elif re.search(r"(Test)? [hH]eadform(\(s\) used)?[.:]", line):
                if re.search(r"headform\s*(\(s\) used)?:", line):
                    data["Headform"] = line.split(":")[1].rstrip().lstrip()
                else:
                    matches = re.split(r"\s+", line)
                    data["Headform"] = matches[-3]

            if re.search("Liner Density", line):
                value = line.split(":")[1].lstrip().rstrip()
                epp_match = re.search(r"\d+[Pp]", value)
                if epp_match:
                    data["EPP Density"] = epp_match[0]
                else:
                    number_match = re.search(r"\d+", value)
                    if number_match:
                        value = number_match[0]
                    data["EPS Density"] = value

            standard_match = re.search(r"([Aa]s per clauses[\s\S]+of [\s\w]+|[Aa]s per[\s\w]+)", line)
            if standard_match:
                match = re.split(r"([Aa]s per clauses[\s\S]+of |[Aa]s per )", standard_match[0])
                data["Standard"] = match[-1].lstrip().rstrip()

            # either 'Limit:<number>g' (possibly with spaces) or 'exceed <number> g' (with or without spaces)
            criteria_match = re.search(r"(Limit:\s*\d+\s*g|exceed\s*\d+\s*g)", line)
            if criteria_match:
                number_match = re.search(r'\d+', criteria_match[0])
                data["Criteria"] = number_match[0]

            if line_check(line, "PDF2"):
                key_value = line.split(":")
                key = key_value[0].rstrip()
                size_text_match = None
                if len(key_value) >= 2:
                    size_text_match = re.search(r"(Small|Medium|Large)", key_value[-2])
                if size_text_match:
                    value = size_text_match[0]
                else:
                    value = str(key_value[-1]).lstrip().rstrip()

                if re.search(r"Helmet Model|Item(/Model)? No\.|Model No\.", line):
                    key = "Model"
                    value = re.search(r"[\w\s]+", value)[0].title()
                if re.search("[Ss]ize", line):
                    key = "Size"
                if re.search(r"\d+\s*-\s*\d+\s*[Cc][Mm]", value):
                    value = re.sub(r"\s+", "", str(value))
                    value = re.search(r"\d+-\d+[Cc][Mm]", str(value))[0].lower()
                data[key] = value

    return data


def parse_pdf3_text(text):
    data = {}
    test_index = 0
    for page in text:
        for line in page.splitlines():
            if not line:
                continue
            key_match = line_check(line, "PDF3")
            if key_match:
                key_value = line.split(":")
                key = key_match[0].lstrip().rstrip()
                data[key] = key_value[1].lstrip().rstrip()

            standard_match = re.search(r"Test\s*Conducted\s*:\s*Based on\s*(Clause\s+\S+\s+of\s+)?[\s\w/]+", line)
            if standard_match:
                data["Standard"] = re.sub(r"Test\s*Conducted\s*:\s*Based on\s*(Clause\s+\S+\s+of\s+)?", "", standard_match[0]).lstrip().rstrip()

            criteria_match = re.search(r"exceed\s+\d+\s*g(\s+peak)?", line)
            if criteria_match:
                number_match = re.search(r"\d+", criteria_match[0])
                data["Criteria"] = number_match[0]

            anvil = is_anvil_type(line.lower())
            if anvil:
                anvil_match = re.search(r"using a {} anvil".format(anvil[0]), line)
                if anvil_match:
                    data["Anvil"] = make_uniform(anvil[0])

            info_row_match = re.search(r"Model:[\S\s]+Size:[\S\s]+(Test\s+)?[Hh]ead(-)?form:[\S\s]+", line)

            # The presence of this row indicates that a test has been performed (there may be plenty)
            if info_row_match:
                # This will also match the trailing blank-spaces and Size text, so these need to be stripped from value
                model_match = re.search(r"Model:[\s\w]+", info_row_match[0])
                # This will also match the trailing blank-spaces and headform text
                size_match = re.search(r"Size:[\s\w-]+", info_row_match[0])
                # This will also match the blank-spaces and HPI part after so these need to be stripped off
                headform_match = re.search(r"(Test\s+)?[Hh]ead(-)?form:[\s\w]+", info_row_match[0])

                data[test_index] = {"Model": (re.sub(r"\s+Size", "", model_match[0]).split(":")[1]).lstrip(),
                                    "Size": re.sub(r"\s+(Test\s+)?[Hh]ead(-)?form", "", size_match[0].split(":")[1]).lstrip(),
                                    "Headform": re.sub(r"\s+HPI(\s*\(from\s+basic\s+plane\))?", "", headform_match[0].split(":")[1]).lstrip().rstrip()
                                    }
                test_index += 1

        if "Criteria" not in data:
            criteria_match = re.search(r"exceed  Details  refer \n\d+\s*g(\s+peak)?", page)
            if criteria_match:
                number_match = re.search(r"\d+", criteria_match[0])
                data["Criteria"] = number_match[0]

    return data


def in_key_set(key):
    return "Standard" in key or "Helmet Size" in key or "Max Peak [g]" in key or "Density" in key


def parse_pdf4_text(text):
    data = {}
    for page in text:
        for line in page.splitlines():
            if not line:
                continue
            if line.startswith("File"):
                break
            if line_check(line, "PDF4"):
                keys = [None, None]
                first_split = line.split(":")
                if len(first_split) >= 2:
                    keys[0] = first_split[0].strip()
                    if len(first_split) == 3:
                        value = re.sub("(Manufacturer|Shock abs. mat.|Density|Helmet Size|Helmet Mass|Job No.)", "",
                                       first_split[1])
                        if in_key_set(keys[0]):
                            data[keys[0]] = value.lstrip().rstrip()

                        key_match = re.search(r"(Manufacturer|Shock abs. mat.|Density|Helmet Size|Helmet Mass|Job No.)",
                                              str(first_split[1]))
                        if key_match:
                            keys[1] = key_match[0]
                            if in_key_set(keys[1]):
                                data[keys[1]] = first_split[len(first_split)-1].strip()
                    else:
                        data[keys[0]] = first_split[1].lstrip().rstrip()
                else:
                    continue
            else:
                continue
    return data


def parse_pdf5_text(text):
    data = {}
    for page in text:
        criteria_match = re.search(r"shall\s+not\s+exceed\s+\d+\s*g\s+peak", page)
        if criteria_match:
            number = re.search(r"\d+", criteria_match[0])[0]
            data["Criteria"] = number
        for line in page.splitlines():
            if not line:
                continue
            if re.search("IMPACT ENERGY ATTENUATION TEST RESULTS", line):
                return data
            key_match = line_check(line, "PDF5")
            if key_match:
                key_value = line.split(":")
                key = key_match[0]
                data[key] = key_value[1].lstrip().rstrip()

    return data


