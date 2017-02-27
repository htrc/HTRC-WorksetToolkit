from builtins import input
def bool_prompt(prompt_str, default=None):
    if default is True:
        default = 'y'
    elif default is False:
        default = 'n'

    result = prompt(prompt_str, options=['y', 'n'], default=default)

    if result == 'y':
        return True
    elif result == 'n':
        return False


def prompt(prompt, options=None, default=None):
    # Construct prompt
    prompt = "\n" + prompt

    if options:
        choices = options[:]
        if default and default in choices:
            default_idx = choices.index(default)
            choices[default_idx] = choices[default_idx].upper()
        prompt += " [{0}]".format('/'.join(choices))
    elif default:
        if isinstance(default,str):
            prompt += " [Default: {0}]".format(default.encode('utf-8'))
        else:
            prompt += " [Default: {0}]".format(default)
    prompt += " "

    # Wait for valid response
    result = None
    while result is None or (options and result not in options):
        result = input(prompt)
        result = result.lower().strip()
        if default and result == '':
            result = default

    return result
