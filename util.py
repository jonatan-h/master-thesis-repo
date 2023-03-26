import re

import Dictionaries


def calculate_safety_factor(peak, criteria):
    return round((float(criteria) / 1.02) / peak, 2) if not peak == 0 else float("NaN")


def determine_result(safety_factor):
    return "PASS" if safety_factor > 1.00 else "FAIL"


def make_uniform(anvil_type):
    if re.search(r"(K[EU]RB|C[EU]RB)", str(anvil_type).upper()):
        return "KERB"
    elif re.search("H(EMI|emi)", str(anvil_type)):
        return "HEMI"
    else:
        return str(anvil_type).upper()


def translate_test_condition(test_condition):
    if re.match(r"(^A$|AMBI[EA]NT|[Aa]mbi[ea]nt|\+20|Room conditioning)", str(test_condition)):  # A, Ambi(e/a)nt or +20
        return "AMBIENT"
    elif re.search(r"(^H$|HIGH|[Hh]igh|HOT|[Hh]ot|\+35)", str(test_condition)):  # H, Hot, High or +35
        return "HOT"
    elif re.search(r"(^L$|LOW|[Ll]ow|COLD|[Cc]old|-25)", str(test_condition)):  # Low, Cold or -25
        return "COLD"
    elif re.search("(^W$|WET|[Ww]et|WATER|[Ww]ater)", str(test_condition)):  # Water or Wet
        return "WET"
    elif re.search(r"(A\s*(I\s*)?G\s*(E\s*)?I\s*N\s*G|[Aa]\s*(i\s*)?g\s*(e\s*)?i\s*n\s*g|ARTIFICIAL|[Aa]rtificial)", str(test_condition)):
        return "AGEING"

    return "N/A"


def standardize_certification(test_type, helmet_type):
    if re.search(r"CPSC(\s*1203)?", str(test_type)):
        return "CPSC";
    elif re.search(r"(^AS$|AS[/\s]*NZS(\s*2062)?)", str(test_type)):
        return "AS/NZS 2063"
    elif re.match("FIS", str(test_type)):
        return "FISRH2013"
    elif match := re.search(r"EN[-\s]*\d+", str(test_type)):
        return re.sub(r"[-\s]+", "", match[0])
    elif match := re.search(r"ASTM[-\s]*\w+", str(test_type)):
        return re.sub(r"[-\s]+", "", match[0])
    elif match := re.search(r"NTA[\s-]*\d+", str(test_type)):
        return re.sub(r"[\s-]+", "", match[0])
    elif re.match(r"CEN$", str(test_type)):
        return "EN1077" if str(helmet_type) == "SNOW" else "EN1078"

    return test_type


def translate_impact_location(impact_location, model, stage_of_testing, certification):
    if re.search(r"(Front|FRONT|front)", impact_location):
        return Dictionaries.front
    elif re.search(r"(Back|BACK|REAR|Rear|rear)", impact_location):
        return Dictionaries.back
    elif re.search(r"([Ll](EFT|eft)|[LlRr](\.)?[Hh](\.)?[Ss]|[LRlr]\.side|[Rr](IGHT|ight))", impact_location):
        return Dictionaries.sides
    elif re.search(r"[Bb](ACK|ack)|[Rr](EAR|ear)", impact_location):
        return Dictionaries.back
    elif re.search(r"[Tt](op|OP)|[Cc](ROWN|rown)", impact_location):
        return Dictionaries.crown

    if stage_of_testing == "Development":
        if re.search(r"(Coron|Kortal|Myelin|Fornix|Orbic|Skull X SPIN|POCito Omne)", model):
            match = re.search(r"\d+$", impact_location)
            if match:
                impact_location = match[0]
        elif re.search("(Corpora|Crane MIPS|Ventral|Artic|Auric|Meninx|Obex|Skull Dura| Skull Dura)", model):
            # in case of hyphens being used, key will be whatever is after the hyphen
            match = re.search(r"[\w\s]+$", impact_location)
            if match:
                impact_location = match[0]
        elif re.search("^Omne", model):
            match = re.search(r"\w+$", impact_location)
            if match:
                impact_location = match[0]
            model = "Omne"
        elif re.search("Axion", model):
            match = re.search(r"\d+", impact_location)
            if match:
                impact_location = match[0]

            if re.search("AS", certification):
                certification = "AS"
            elif re.search(r"EN\d+", certification):
                certification = "CE"
            # CSPC already correctly formatted for Dictionary

            try:
                loc = Dictionaries.revised_impact_locations[stage_of_testing][model][certification][impact_location]
            except KeyError as e:
                print("Impact location not found: {}".format(e))
                return "N/A"
            return loc

        elif re.search("Otocon", model):
            match = re.search(r"\d+", impact_location)
            if match:
                impact_location = match[0]

            if re.search("ASTM", certification):
                certification = "ASTM"
            elif re.search("AS", certification):
                certification = "AS"
            elif re.search(r"EN\d+", certification):
                certification = "CE"

            # CPSC is already formatted correctly for Dictionary lookup by default

            elif re.search("NTA", certification):
                certification = "NTA"

            try:
                loc = Dictionaries.revised_impact_locations[stage_of_testing][model][certification][impact_location]
            except KeyError as e:
                print("Impact location not found: {}".format(e))
                return "N/A"
            return loc

        elif re.search("(Tectal|Octal)",  model):
            match = re.search(r"\d+$", impact_location)
            if match:
                impact_location = match[0]

            if re.search(r"EN\d+", certification):
                certification = "CE"
            elif re.search(r"AS/NZ", certification):
                certification = "AS"

            # CPSC certification is already of correct format
            try:
                loc = Dictionaries.revised_impact_locations[stage_of_testing][model][certification][impact_location]
            except KeyError as e:
                print("Impact location not found: {}".format(e))
                return "N/A"
            return loc

        try:
            location = Dictionaries.revised_impact_locations[stage_of_testing][model][impact_location]
        except KeyError as e:
            print("Impact location not found: {}".format(e))
            return "N/A"
        return location
    elif stage_of_testing == "BatchTesting" or stage_of_testing == "Certificates":
        try:
            location = Dictionaries.revised_impact_locations[stage_of_testing][impact_location]
        except KeyError as e:
            print("Impact location not found: {}".format(e))
            return "N/A"
        return location

    return "N/A"


def get_helmet_type(model):
    if re.search(r"(Axion|Coron|Corpora|Crane|Kortal|Myelin|Octal|Omne|Otocon|Tectal|Ventral)", model):
        return "CYCLING"
    elif re.search(r"(Artic|Auric|Fornix|Meninx|Obex|Skull)", model):
        return "SNOW"
    else:
        return "N/A"


def is_anvil_type(string):
    return re.search(r"(flat|curb|kerb|hemi|edge)", string)
