import os
from bs4 import BeautifulSoup
from pyjsparser import parse
import packer_detector.features
import packer_detector.config
import packer_detector.packers_signatures


def signatures_execution(parsed_js):
    try:
        eval_res = packer_detector.packers_signatures.detect_eval_unescape(parsed_js)
        aes_res = packer_detector.packers_signatures.detect_aes_ctr_decrypt(parsed_js)

        print('detect_eval_unescape', ":", eval_res)
        print('detect_aes_ctr_decrypt', ":", aes_res)

        if eval_res or aes_res:
            return True
        return False
    except Exception as e:
        print(e)
        return True

def features_collection_execution(js_code_block, parsed_js, identifiers, js_var_values):
    try:
        num_line_breaks = packer_detector.features.num_line_breaks(js_code_block)

        all_statement = packer_detector.features.all_statement(parsed_js)
        switch_case = packer_detector.features.switch_case(parsed_js)
        for_statement = packer_detector.features.for_statement(parsed_js)
        while_statement = packer_detector.features.while_statement(parsed_js)
        if_statement = packer_detector.features.if_statement(parsed_js)

        num_unique_identifiers = packer_detector.features.num_unique_identifiers(identifiers)
        num_identifiers = packer_detector.features.num_identifiers(identifiers)
        number_of_0x_identifier = packer_detector.features.number_of_0x_identifier(identifiers)
        number_of_hex_identifier = packer_detector.features.number_of_hex_identifier(identifiers)

        for feature_type in packer_detector.config.LIST_OF_FEATURES:
            for feature_def in packer_detector.config.get_config(feature_type):
                feature_value = getattr(packer_detector.features, feature_def)(locals()[packer_detector.config.get_config("LIST_OF_FEATURES")[feature_type]])
                print('features_collection_execution: ', feature_def, feature_value)

        if all_statement != 0 and (switch_case/all_statement > 0.1 \
            or for_statement/all_statement > 0.1 \
            or while_statement/all_statement > 0.1 \
            or if_statement/all_statement > 0.1):
                return True
            
        if all_statement != 0 and num_line_breaks/all_statement < 0.25:
            return True

        if num_identifiers != 0 and num_unique_identifiers/num_identifiers > 0.25:
            return True

        if num_identifiers != 0 and number_of_0x_identifier/num_identifiers > 0.05:
            return True

        if num_identifiers != 0 and number_of_hex_identifier/num_identifiers > 0.05:
            return True

        return False
    except Exception as e:
        print(e)
        return True

def check_script(js_code):
    try:
        parsed_js = parse(js_code)
        identifiers = packer_detector.features.identifiers(parsed_js)
        js_var_values = packer_detector.features.var_values_extract(parsed_js)

        res_feature = features_collection_execution(js_code, parsed_js, identifiers, js_var_values)
        res_signature = signatures_execution(parsed_js)

        if res_feature or res_signature:
            return True
        return False
    except Exception as e:
        print(e)
        return True

def scan_script(script):
    try:
        result = check_script(script)
        return result
    except Exception as e:
        print(e)
        return True
