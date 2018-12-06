#!/usr/bin/env python3
import os
import re
from subprocess import Popen, PIPE
from globbing import glob_string
from path_expansions import path_expansions
from parse_command_shell import Token


def handle_logic_op(string, *, output=True):
    '''
    Tasks: + First get step need to do from parse command operator
           + Run command and if exit status isn't 0 and operator is 'and' then skip
           + else exit status is 0 and operator is 'or' then skip
    '''
    steps_exec = parse_command_operator(Token(string).split_token())
    operator = ''
    result = []
    for i, step in enumerate(steps_exec):
        command = step[0]
        op = step[1]
        if is_skip_command(i, operator) and is_boolean_command(command[0]):
            # run command with arguments
            result.append(handle_exit_status(' '.join(step[0])))
        operator = op
    return result


def is_skip_command(index, operator):
    if operator == '&&':
        return index == 0 or os.environ['?'] == '0'
    return index == 0 or os.environ['?'] != '0'


def is_boolean_command(command):
    if command == 'false':
        os.environ['?'] = '1'
    elif command == 'true':
        os.environ['?'] = '0'
    else:
        return True
    return False


def parse_command_operator(string):
    '''
    Tasks: + Split command and logical operator into list of tuple
           + Inside tuple is command + args and logical operators after that command
           + Return list of step need to do logical operators
    '''
    steps = []
    commands = string + [" "]
    start = 0
    for i, com in enumerate(commands):
        if com == '||' or com == "&&" or com == ' ':
            steps.append((commands[start: i], commands[i]))
            start = i + 1
    return steps


def builtins_cd(directory=''):  # implement cd
    if directory:
        try:
            os.environ['OLDPWD'] = os.getcwd()
            os.chdir(directory)  # change working directory
            os.environ['PWD'] = os.getcwd()
            exit_value, output = 0, ''
        except FileNotFoundError:
            exit_value, output = 1, 'intek-sh: cd: %s: No ' \
                                       'such file or directory\n' % directory
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
                              'not a valid identifier\n' % variable)
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
            errors.append('intek-sh: unset: `%s\': not a valid identifier\n' % variable)
        elif variable in os.environ:
            os.environ.pop(variable)
    return exit_value, '\n'.join(errors)


def builtins_exit(exit_code):  # implement exit
    global loop
    exit_value = 0
    output = []
    output.append('exit')
    if exit_code:
        if exit_code.isdigit():
            exit_value = int(exit_code)
        else:
            output.append('intek-sh: exit: ' + exit_code)
    loop = False
    return exit_value, '\n'.join(output)


def run_command(command, whatever=[], inp=None):
    global process
    exit_value = 0
    output = []
    builtins = ('cd', 'printenv', 'export', 'unset', 'exit')
    if command in builtins:
        if command == 'cd':
            return builtins_cd(' '.join(whatever))
        elif command == 'printenv':
            return builtins_printenv(' '.join(whatever))
        elif command == 'export':
            return builtins_export(' '.join(whatever))
        elif command == 'unset':
            return builtins_unset(' '.join(whatever))
        else:
            return builtins_exit(' '.join(whatever))
    if '/' in command:
        try:
            process = Popen([command]+whatever, stdin=inp, stdout=PIPE, stderr=PIPE)
            out, err = process.communicate()  # byte
            process.wait()
            exit_value = process.returncode
            if err:
                output.append(err.decode())
            if out:
                output.append(out.decode())
        except PermissionError:
            exit_value = 126
            output.append('intek-sh: %s: Permission denied\n' % command)
        except FileNotFoundError:
            exit_value = 127
            output.append('intek-sh: %s: command not found\n' % command)
    elif 'PATH' in os.environ:
        paths = os.environ['PATH'].split(':')
        not_found = True
        for path in paths:
            realpath = path + '/' + command
            if os.path.exists(realpath):
                not_found = False
                process = Popen([realpath]+whatever, stdin=inp, stdout=PIPE, stderr=PIPE)
                out, err = process.communicate()  # byte
                process.wait()
                exit_value = process.returncode
                if err:
                    output.append(err.decode())
                if out:
                    output.append(out.decode())
                break
        if not_found:
            exit_value = 127
            output.append('intek-sh: %s: command not found\n' % command)
    else:
        exit_value = 127
        output.append('intek-sh: %s: command not found\n' % command)
    return exit_value, '\n'.join(output)


def handle_exit_status(string):
    if '$' in string or '~' in string:
        exit_value, string = path_expansions(string)
        if exit_value:
            os.environ['?'] = str(exit_value)
            return string
    if '*' in string or '?' in string:
        string = glob_string(string)
    command = string.split()[0]
    args = string[len(command):].split()
    exit_value, output = run_command(command, args)
    os.environ['?'] = str(exit_value)
    return output


def main():
    global loop
    os.environ['?'] = '0'
    loop = True
    while loop:
        try:
            whatever = input('intek-sh$ ')
            handle_logic_op(whatever)
        except IndexError:
            pass
        except EOFError:
            loop = False


if __name__ == '__main__':
    main()
