#!/usr/bin/env python3
import os
import re
from subprocess import Popen, PIPE
from globbing import glob_string
from path_expansions import path_expansions


def builtins_cd(directory=''):  # implement cd
    if directory:
        try:
            os.environ['OLDPWD'] = os.getcwd()
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
            os.environ['OLDPWD'] = os.getcwd()
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
                errors.append('intek-sh: export: `%s\': '
                              'not a valid identifier' % variable)
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


def builtins_exit(exit_code):  # implement exit
    global w_loop
    exit_value = 0
    output = []
    output.append('exit')
    if exit_code:
        if exit_code.isdigit():
            exit_value = int(exit_code)
        else:
            output.append('intek-sh: exit: ' + exit_code)
    w_loop = False
    return exit_value, '\n'.join(output)


def run_single_command(command, whatever='', inp=None):
    exit_value = 0
    output = []
    builtins = ('cd', 'printenv', 'export', 'unset', 'exit')
    if command in builtins:
        whatever = whatever.strip()
        if command == 'cd':
            return builtins_cd(whatever)
        elif command == 'printenv':
            return builtins_printenv(whatever)
        elif command == 'export':
            return builtins_export(whatever)
        elif command == 'unset':
            return builtins_unset(whatever)
        else:
            return builtins_exit(whatever)
    if '/' in command:
        try:
            process = Popen(command+whatever, stdin=inp, stdout=PIPE, stderr=PIPE, shell=True)
            out, err = process.communicate()  # byte
            if err:
                exit_value = 1
                output.append(err.decode())
            if out:
                output.append(out.decode())
        except PermissionError:
            exit_value = 126
            output.append('intek-sh: %s: Permission denied' % command)
        except FileNotFoundError:
            exit_value = 127
            output.append('intek-sh: %s: command not found' % command)
    elif 'PATH' in os.environ:
        paths = os.environ['PATH'].split(':')
        not_found = True
        for path in paths:
            realpath = path + '/' + command
            if os.path.exists(realpath):
                not_found = False
                process = Popen(realpath+whatever, stdin=inp, stdout=PIPE, stderr=PIPE, shell=True)
                out, err = process.communicate()  # byte
                if err:
                    exit_value = 1
                    output.append(err.decode())
                if out:
                    output.append(out.decode())
                break
        if not_found:
            exit_value = 127
            output.append('intek-sh: %s: command not found' % command)
    else:
        exit_value = 127
        output.append('intek-sh: %s: command not found' % command)
    return exit_value, '\n'.join(output)


def run_pipes(string):
    regex = r'(?<!\|)\|(?!\|)'
    pipes = re.split(regex, string)
    exit_value = 0
    input = None
    for pipe in pipes:
        if '$' in pipe or '~' in pipe:
            exit_value, pipe = path_expansions(pipe)
            if exit_value:
                os.environ['?'] = str(exit_value)
                return exit_value, pipe
        command = pipe.split()[0]
        args = pipe[len(command):]
        if '*' in args or '?' in args:
            args = glob_string(args)
        if not exit_value:
            exit_value, input = run_single_command(command, args, input)
        else:
            return exit_value, input
    return exit_value, input


def run_shell(string):
    # redirection_operators = ('>', '>>', '<')
    os.environ['?'] = '0'
    exit_value = 0
    if '$' in string or '~' in string:
        exit_value, string = path_expansions(string)
        if exit_value:
            os.environ['?'] = str(exit_value)
            return string
    exit_value, output = run_pipes(string)
    if exit_value:
        os.environ['?'] = str(exit_value)
    return output


def main():
    builtins = ('cd', 'printenv', 'export', 'unset', 'exit')
    loop = True
    while loop:
        try:
            whatever = input('intek-sh$ ')
            while not whatever:
                whatever = input('intek-sh$ ')
            print(run_shell(whatever))
        except EOFError:
            loop = False


if __name__ == '__main__':
    main()
