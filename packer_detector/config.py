import argparse

LIST_OF_SIGNATURES = ['detect_aes_ctr_decrypt', 'detect_eval_unescape']
LIST_OF_JS_CODE_FEATURES = ['num_line_breaks']
LIST_OF_JS_AST_CODE_FEATURES = ['all_statement', 'switch_case', 'for_statement', 'while_statement', 'if_statement']
LIST_OF_JS_IDENTIFIERS_FEATURES = ['num_unique_identifiers', 'num_identifiers', 'number_of_0x_identifier', 'number_of_hex_identifier']
LIST_OF_FEATURES = {'LIST_OF_JS_CODE_FEATURES': 'js_code_block', 'LIST_OF_JS_AST_CODE_FEATURES': 'parsed_js', 'LIST_OF_JS_IDENTIFIERS_FEATURES': 'identifiers'}


def get_config(name):
    return globals()[name]

