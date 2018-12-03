#!/usr/bin/env python3
import os
import subprocess


def builtins_cd(directory=''):  # implement cd
    if directory:
        try:
            os.chdir(directory)  # change working directory
            os.environ['PWD'] = os.getcwd()
            exit_value, output = 0, ''
        except FileNotFoundError:
            exit_value, output = 1, 'intek-sh: cd: %s: No ' \
                                       'such file or directory' % directory
    else:  # if variable directory is empty, change working dir into homepath
        if 'HOME' not in os.environ:
            exit_value, output = 1, 'intek-sh: cd: HOME not set'
        else:
            homepath = os.environ['HOME']
            os.chdir(homepath)
            os.environ['PWD'] = os.getcwd()
            exit_value, output = 0, ''
    return exit_value, output


def builtins_printenv(variables=''):  # implement printenv
    exit_value = 0
    output_lines = []
    if variables:
        for variable in variables.split():
            if variable in os.environ:
                output_lines.append(os.environ[variable])
            else:
                exit_value = 1
    else:  # if variable is empty, print all envs
        for key, value in os.environ.items():
            output_lines.append(key + '=' + value)
    return exit_value, '\n'.join(output_lines)


def check_name(name):
    # check if name is a valid identifier or not
    if not name or name[0].isdigit():
        return False
    for char in name:
        if not (char.isalnum() or char is '_'):
            return False
    return True


def builtins_export(variables=''):  # implement export
    exit_value = 0
    if variables:
        errors = []
        for variable in variables.split():
            if '=' in variable:
                name, value = variable.split('=', 1)
            else:  # if variable stands alone, set its value as ''
                name = variable
                value = ''
            if check_name(name):
                os.environ[name] = value
            else:
                exit_value = 1
                errors.append('intek-sh: export: `%s\': not a valid identifier' % variable)
        output = '\n'.join(errors)
    else:
        env = builtins_printenv()[1].split('\n')
        result = []
        for line in env:
            result.append('declare -x ' + line.replace('=', '=\"', 1) + '\"')
        output = '\n'.join(result)
    return exit_value, output


def builtins_unset(variables=''):  # implement unset
    exit_value = 0
    errors = []
    for variable in variables.split():
        if not check_name(variable):
            exit_value = 1
            errors.append('intek-sh: unset: `%s\': not a valid identifier' % variable)
        elif variable in os.environ:
            os.environ.pop(variable)
    return exit_value, '\n'.join(errors)


# def builtins_exit(exit_code):  # implement exit
#     global w_loop
#     w_loop = False
#     print('exit')
#     if exit_code:
#         try:
#             sys.exit(int(exit_code))
#         except ValueError:
#             print('intek-sh: exit: ', end='')
#             sys.exit(exit_code)
#     else:
#         sys.exit()


def builtins_run(command, whatever):
    exit_value = 0
    errors = []
    if '/' in command:
        try:
            subprocess.run(command)
        except PermissionError:
            exit_value = 1
            errors.append('intek-sh: %s: Permission denied' % command)
        except FileNotFoundError:
            exit_value = 127
            errors.append('intek-sh: %s: command not found' % command)
    elif 'PATH' in os.environ:
        paths = os.environ['PATH'].split(':')
        not_found = True
        for path in paths:
            realpath = path + '/' + command
            if os.path.exists(realpath):
                not_found = False
                for arg in whatever:
                    process = subprocess.Popen([realpath]+arg, stdout=subprocess.PIPE)

                # process = subprocess.Popen([realpath]+whatever, stdout=subprocess.PIPE)
                # process.wait()
                break
        if not_found:
            exit_value = 127
            errors.append('intek-sh: %s: command not found' % command)
    else:
        exit_value = 127
        errors.append('intek-sh: %s: command not found' % command)
    if not exit_value:
        output = '\n'.join(errors)
    return exit_value, output


def main():
    builtins = ('cd', 'printenv', 'export', 'unset', 'exit')
    loop = True
    while loop:
        try:
            whatever = input('intek-sh$ ').strip(' ').split()
            while not whatever:
                whatever = input('intek-sh$ ').strip(' ').split()
            command = whatever.pop(0)
            if command in builtins:
                exec('builtins_%s(\' \'.join(whatever))' % command)
            else:
                builtins_run(command, whatever)
        except EOFError:
            loop = False


# os.environ[?] = exit_value
# option return stdout


if __name__ == '__main__':
    main()
