#!/usr/bin/env python3

from os import path, getenv
from built_ins import check_name


def expand_tilde(arg):
    # expand tilde
    cur_path = getenv('PWD')
    old_path = getenv('OLDPWD')
    arg = path.expanduser(arg)
    if (arg == '~+' or arg.startswith('~+/')) and cur_path:
        arg = arg.replace('~+', cur_path, 1)
    if (arg == '~-' or arg.startswith('~-/')) and old_path:
        arg = arg.replace('~-', old_path, 1)
    return arg


def tilde_expansions(string):
    # tilde expansions
    args = string.split()
    for i, arg in enumerate(args):
        if '~' in arg:
            if '=' in arg:
                key, new_args = arg.split('=', 1)
                if check_name(key):
                    args[i] = key + '=' + ':'.join([expand_tilde(x) for
                                                    x in new_args.split(':')])
            else:
                args[i] = expand_tilde(arg)
    return ' '.join(args)


def parameter_expansions(string):
    # parameter expansions
    exit_value = 0
    string = path.expandvars(string)
    while '$' in string:
        if '${' in string:
            name = string[string.find('${')-1:string.find('}')+1]
            if check_name(name[3:-1]):
                string = string[:string.find('${')-1] + \
                         string[string.find('}')+1:]
                continue
            else:
                exit_value = 1
                string = 'bash: %s: bad substitution' % name
                return exit_value, string
        j = string.index('$') + 1
        while j < len(string) and string[j] and \
                (string[j].isalnum() or string[j] == '_'):
            j += 1
        string = string[:string.index('$')] + string[j:]
    return exit_value, string


def path_expansions(string):
    exit_value = 0
    if '~' in string:
        string = tilde_expansions(string)
    if '$' in string:
        exit_value, string = parameter_expansions(string)
    return exit_value, string