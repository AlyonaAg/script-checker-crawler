import os
from bs4 import BeautifulSoup
from pyjsparser import parse
import packer_detector.features
import packer_detector.config
import packer_detector.packers_signatures


def signatures_execution(parsed_js):
    try:
        detection_print_values = {}
        for detection_def in config.LIST_OF_SIGNATURES:
            detection_value = getattr(packers_signatures, detection_def)(parsed_js)
            print(detection_def, ":", detection_value)
            detection_print_values[detection_def] = detection_value
    except Exception as e:
        print(e)

def features_collection_execution(js_code_block, parsed_js, identifiers, js_var_values):
    try:
        for feature_type in config.LIST_OF_FEATURES:
            for feature_def in config.get_config(feature_type):
                feature_value = getattr(features, feature_def)(locals()[config.get_config("LIST_OF_FEATURES")[feature_type]])
                print(feature_type, feature_value)
    except Exception as e:
        print(e)

def check_script(js_code):
    result = False
    try:
        parsed_js = parse(js_code)
        identifiers = features.unique_identifiers(parsed_js)
        js_var_values = features.var_values_extract(parsed_js)
        features_collection_execution(js_code, parsed_js, identifiers, js_var_values)
        signatures_execution(parsed_js)
    except Exception as e:
        print(e)
    return result

def scan_script(script):
    try:
        result = check_script(script)
        return result
    except Exception as e:
        print(e)
