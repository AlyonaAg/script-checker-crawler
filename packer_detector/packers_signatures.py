import dpath.util


def detect_eval_unescape(parsed_js):
    try:
        if 'ExpressionStatement' in dpath.util.values(parsed_js, 'body/*/type'):
            if 'eval' in dpath.util.values(parsed_js, 'body/*/expression/callee/name'):
                return True
        return False
    except Exception as e:
        print(e)
        return True


def detect_aes_ctr_decrypt(parsed_js):
    try:
        if 'VariableDeclaration' in dpath.util.values(parsed_js, 'body/*/type'):
            if 'Aes' in dpath.util.values(parsed_js, 'body/*/declarations/*/init/callee/object/object/name') and \
                    'Ctr' in dpath.util.values(parsed_js, 'body/*/declarations/*/init/callee/object/property/name') and \
                    'decrypt' in dpath.util.values(parsed_js, 'body/*/declarations/*/init/callee/property/name'):
                return True
        return False
    except Exception as e:
        print(e)
        return True