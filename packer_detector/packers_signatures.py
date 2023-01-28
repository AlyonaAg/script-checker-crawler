import dpath.util


def detect_push_shift_obfuscation_func(parsed_js):
    try:
        if 'BlockStatement' in dpath.util.values(parsed_js, 'body/*/expression/callee/body/type'):
            if 'push' in dpath.util.values(parsed_js, 'body/*/expression/callee/body/body/*/declarations/*/init/body/body/*/body/body/*/expression/callee/property/value'):
                if 'shift' in dpath.util.values(parsed_js, 'body/*/expression/callee/body/body/*/declarations/*/init/body/body/*/body/body/*/expression/arguments/*/callee/property/value'):
                    return 'shift_push_obfuscation_func'
        return 'no_obfuscation'
    except Exception as e:
        print(e)
        return 'no_obfuscation'


def detect_eval_unescape(parsed_js):
    try:
        if 'ExpressionStatement' in dpath.util.values(parsed_js, 'body/*/type'):
            if 'eval' in dpath.util.values(parsed_js, 'body/*/expression/callee/name'):
                if 'unescape' in dpath.util.values(parsed_js, 'body/*/expression/arguments/*/callee/name'):
                    return "eval_unescape_packer_match"
        return 'no_obfuscation'
    except Exception as e:
        print(e)
        return 'no_obfuscation'


def detect_aes_ctr_decrypt(parsed_js):
    try:
        if 'VariableDeclaration' in dpath.util.values(parsed_js, 'body/*/type'):
            if 'Aes' in dpath.util.values(parsed_js, 'body/*/declarations/*/init/callee/object/object/name') and \
                    'Ctr' in dpath.util.values(parsed_js, 'body/*/declarations/*/init/callee/object/property/name') and \
                    'decrypt' in dpath.util.values(parsed_js, 'body/*/declarations/*/init/callee/property/name'):
                return "aes_ctr_decrypt_packer_match"
        return 'no_obfuscation'
    except Exception as e:
        print(e)
        return 'no_obfuscation'