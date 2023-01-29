import re
import dpath.util


COLLECT_VARS_AND_FUNC_REGEX = "'type':\s+u?'([^']+)', 'name':\su?'([^']+)'"
COLLECT_SWITCH_STATEMENT = "'type': 'SwitchStatement'"
COLLECT_FOR_STATEMENT = "'type': 'ForStatement'"
COLLECT_WHILE_STATEMENT = "'type': 'WhileStatement'"
COLLECT_IF_STATEMENT = "'type': 'IfStatement'"
COLLECT_ALL_STATEMENT = "'type': '([a-zA-Z]+)Statement'"
CHECK_IDENTIFIER_HEX_REGEX = r'(\\x[0-9a-z][0-9a-z]){4,}'
COUNT_LINE_BREAKS = r'(\n)'


def num_line_breaks(js):
    return len(line_breaks(js))

def line_breaks(js):
    try:
        x = re.findall(COUNT_LINE_BREAKS, str(js), re.DOTALL)
    except Exception as e:
        print(e)
        return None
    return x

def switch_case(parsed_js):
    return len(collect_switch_case(parsed_js))

def collect_switch_case(parsed_js):
    try:
        x = re.findall(COLLECT_SWITCH_STATEMENT, str(parsed_js), re.DOTALL)
    except Exception as e:
        print(e)
        return None
    return x

def for_statement(parsed_js):
    return len(collect_for_statement(parsed_js))

def collect_for_statement(parsed_js):
    try:
        x = re.findall(COLLECT_FOR_STATEMENT, str(parsed_js), re.DOTALL)
    except Exception as e:
        print(e)
        return None
    return x

def while_statement(parsed_js):
    return len(collect_while_statement(parsed_js))

def collect_while_statement(parsed_js):
    try:
        x = re.findall(COLLECT_WHILE_STATEMENT, str(parsed_js), re.DOTALL)
    except Exception as e:
        print(e)
        return None
    return x

def if_statement(parsed_js):
    return len(collect_if_statement(parsed_js))

def collect_if_statement(parsed_js):
    try:
        x = re.findall(COLLECT_IF_STATEMENT, str(parsed_js), re.DOTALL)
    except Exception as e:
        print(e)
        return None
    return x

def all_statement(parsed_js):
    return len(collect_all_statement(parsed_js))

def collect_all_statement(parsed_js):
    try:
        x = re.findall(COLLECT_ALL_STATEMENT, str(parsed_js), re.DOTALL)
    except Exception as e:
        print(e)
        return None
    return x

def identifiers(parsed_js):
    try:
        js_identifiers = []
        for i in collect_func_var_names(parsed_js):
            js_identifiers.append(i)
        return js_identifiers
    except Exception as e:
        print(e)

def num_unique_identifiers(js_identifiers):
    return len(set(js_identifiers))

def num_identifiers(js_identifiers):
    return len(js_identifiers)

def num_unique_var_values(js_var_values):
    return len(js_var_values)

def check_identifier_0x(x):
    if x.startswith('_0x'):
        return True
    return False

def check_identifier_hex(x):
    try:
        hex_encoded_identifiers = re.search(CHECK_IDENTIFIER_HEX_REGEX, str(x))
        if hex_encoded_identifiers:
            return True
        return False
    except Exception as e:
        print(e)
        pass

def collect_func_var_names(parsed_js):
    try:
        x = re.findall(COLLECT_VARS_AND_FUNC_REGEX, str(parsed_js), re.DOTALL)
    except Exception as e:
        print(e)
        return None
    return x

def var_values_extract(parsed_js):
    try:
        values = []
        if dpath.util.values(parsed_js, 'body/*/declarations/*/init/elements/*/raw'):
            values = [x.strip('\'') for x in dpath.util.values(parsed_js, 'body/*/declarations/*/init/elements/*/raw')]
        elif dpath.util.values(parsed_js, 'body/*/body/body/*/declarations/*/init/elements/*/raw'):
            values = [x.strip('\'') for x in dpath.util.values(parsed_js, 'body/*/body/body/*/declarations/*/init/elements/*/raw')]
        return(values)
    except Exception as e:
        print(e)
        pass

def number_of_0x_identifier(identifiers):
    try:
        number_of_0x_identifiers = 0
        for id in identifiers:
            if check_identifier_0x(id[1]):
                number_of_0x_identifiers += 1
        return number_of_0x_identifiers
    except Exception as e:
        print(e)
        return None

def number_of_hex_identifier(identifiers):
    try:
        number_of_hex_identifiers = 0
        for id in identifiers:
            if check_identifier_hex(id[1]):
                number_of_hex_identifiers += 1
        return number_of_hex_identifiers
    except Exception as e:
        print(e)
        return None


def js_blocks_declarations(parsed_js):
    try:
        return dpath.util.values(parsed_js, 'body/*/type')
    except Exception as e:
        print(e)
        pass
