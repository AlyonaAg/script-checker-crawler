import argparse

LIST_OF_SIGNATURES = ['detect_push_shift_obfuscation_func', 'detect_push_shift_v2_obfuscation_func', 'detect_munger_packer', 'detect_aes_ctr_decrypt', 'detect_eval_unescape']
LIST_OF_JS_AST_CODE_FEATURES = ['num_unique_identifiers']
LIST_OF_JS_IDENTIFIERS_FEATURES = ['number_of_0x_identifier', 'number_of_hex_identifier']
LIST_OF_JS_VAR_VALUES_FEATURES = ['num_unique_var_values', 'number_of_0x_var', 'number_of_hex_var']
LIST_OF_FEATURES = {'LIST_OF_JS_CODE_FEATURES': 'js_code_block', 'LIST_OF_JS_AST_CODE_FEATURES': 'parsed_js', 'LIST_OF_JS_IDENTIFIERS_FEATURES': 'identifiers', 'LIST_OF_JS_VAR_VALUES_FEATURES': 'js_var_values'}


def get_config(name):
    return globals()[name]

