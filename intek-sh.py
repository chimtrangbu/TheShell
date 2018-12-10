#!/usr/bin/env python3
from command_line import Shell, write_file
import os
import sys
import curses
from subprocess import Popen, PIPE
from globbing import glob_string
from path_expansions import path_expansions
from parse_command_shell import Token
from signal import SIG_IGN, SIGINT, SIGQUIT, SIGTSTP, signal


def handle_logic_op(string, isprint=False, operator=None):
    '''
    Tasks:
    - First get step need to do from parse command operator
    - Run command and if exit status isn't 0 and operator is 'and' then skip
    - Else exit status is 0 and operator is 'or' then skip
    - After handle command substituition then run exit status of command
    '''
    steps_exec = parse_command_operator(Token(string).split_token())
    output = []
    printf(str(steps_exec))
    for command, next_op in steps_exec:
        if is_skip_command(operator) and is_boolean_command(command[0]):
            command = handle_com_substitution(command)
            result = handle_exit_status(' '.join(command))
            if result and isprint:
                printf(result)
            output.append(result)
        operator = next_op
    return output


def handle_com_substitution(arguments):
    '''
    Tasks:
    - Checking is command substitution return string between backquote else return origin argument passed
    - If string isn't empty then run handle logical operator to get result of that command
    - If string is empty not need do anthing
    '''
    new_command = []
    for arg in arguments:
        result = check_command_sub(arg)
        if result and result != arg:
            valids = [arg for arg in handle_logic_op(result) if arg]
            new_command += [e for arg in valids for e in arg.split('\n')]
        elif result:
            new_command.append(arg)
    return new_command


def check_command_sub(arg):
    if arg.startswith('`') and arg.endswith('`'):
        return arg[1:-1:].strip()
    if arg.startswith('\\`') and arg.endswith('\\`'):
        return arg[2:-2:].strip()
    return arg


def is_skip_command(operator):
    if not operator:
        return True
    if operator == '&&':
        return os.environ['?'] == '0'
    return os.environ['?'] != '0'


def is_boolean_command(command):
    if command == 'false':
        os.environ['?'] = '1'
    elif command == 'true':
        os.environ['?'] = '0'
    else:
        return True
    return False


def parse_command_operator(args):
    '''
    Tasks:
    - Split command and logical operator into list of tuple
    - Inside tuple is command + args and next logical operators after command
    - Return list of step need to do logical operators
    '''
    steps = []
    commands = args + [" "]
    start = 0
    for i, com in enumerate(commands):
        if com == '||' or com == "&&" or com == ' ':
            steps.append((commands[start: i], commands[i]))
            start = i + 1
    return steps


def builtins_cd(directory=''):  # implement cd
    exit_value = 0
    if directory:
        try:
            os.environ['OLDPWD'] = os.getcwd()
            os.chdir(directory)  # change working directory
            os.environ['PWD'] = os.getcwd()
        except FileNotFoundError:
            exit_value, error = 1, 'intek-sh: cd: %s: No ' \
                'such file or directory' % directory
    else:  # if variable directory is empty, change working dir into homepath
        if 'HOME' not in os.environ:
            exit_value, error = 1, 'intek-sh: cd: HOME not set'
        else:
            os.environ['OLDPWD'] = os.getcwd()
            homepath = os.environ['HOME']
            os.chdir(homepath)
            os.environ['PWD'] = os.getcwd()
    if exit_value:
        show_error(error)
    return exit_value, ''


def builtins_printenv(variables=[]):  # implement printenv
    exit_value = 0
    output_lines = []
    if variables:
        for variable in variables:
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


def builtins_export(variables=[]):  # implement export
    exit_value = 0
    if variables:
        for variable in variables:
            if '=' in variable:
                name, value = variable.split('=', 1)
            else:  # if variable stands alone, set its value as ''
                name = variable
                value = ''
            if check_name(name):
                os.environ[name] = value
            else:
                exit_value = 1
                show_error('intek-sh: export: `%s\': '
                           'not a valid identifier' % variable)
    else:
        env = builtins_printenv()[1].split('\n')
        output = []
        for line in env:
            output.append('declare -x ' + line.replace('=', '=\"', 1) + '\"')
    return exit_value, '\n'.join(output)


def builtins_unset(variables=[]):  # implement unset
    exit_value = 0
    for variable in variables:
        if not check_name(variable):
            exit_value = 1
            show_error(
                'intek-sh: unset: `%s\': not a valid identifier' % variable)
        elif variable in os.environ:
            os.environ.pop(variable)
    return exit_value, ''


def builtins_exit(exit_code):  # implement exit
    global shell
    printf('exit')
    curses.endwin()
    exit_value = 0
    if exit_code:
        if exit_code.isdigit():
            exit_value = int(exit_code)
        else:
            printf('intek-sh: exit: ' + exit_code)
    shell.write_history_file()
    sys.exit(exit_value)


def run_executions(command, args, input):
    output = []
    try:
        process = Popen([command]+args, stdin=input, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()  # byte
        process.wait()
        exit_value = process.returncode
        if err:
            message = err.decode()
        if out:
            output.append(out.decode())
    except PermissionError:
        exit_value = 126
        message = 'intek-sh: %s: Permission denied' % command
    except FileNotFoundError:
        exit_value = 127
        message = 'intek-sh: %s: command not found' % command
    if exit_value:
        show_error(message)
    return exit_value, ''.join(output)


def run_command(command, args=[], inp=None):
    if command == 'cd':
        return builtins_cd(' '.join(args))
    elif command == 'printenv':
        return builtins_printenv(args)
    elif command == 'export':
        return builtins_export(args)
    elif command == 'unset':
        return builtins_unset(args)
    elif command == 'exit':
        return builtins_exit(' '.join(args))
    elif '/' in command:
        return run_executions(command, args, inp)
    elif 'PATH' in os.environ:
        paths = os.environ['PATH'].split(':')
        for path in paths:
            realpath = path + '/' + command
            if os.path.exists(realpath):
                return run_executions(realpath, args, inp)
    show_error('intek-sh: %s: command not found' % command)
    return 127, ''


def handle_exit_status(string):
    if '$' in string or '~' in string:
        exit_value, string = path_expansions(string)
        if exit_value:
            os.environ['?'] = str(exit_value)
            show_error(string)
            return ''
    if '*' in string or '?' in string:
        string = glob_string(string)
    args = Token(string, keep_quote=False).split_token()
    command = args.pop(0)
    exit_value, output = run_command(command, args)
    os.environ['?'] = str(exit_value)
    return output


def printf(string, end='\n'):
    '''
    Tasks:
    - Support print string on screen of curses module
    '''
    global shell
    shell.printf(string, end)


def setup_terminal():
    global shell
    shell = Shell()
    os.environ['?'] = '0'


def handle_signal(sig, frame):
    if sig == SIGINT:
        printf('^C')
        exit_code = '130'
    elif sig == SIGQUIT:
        printf('^\\')
        exit_code = '131'
    else:
        printf('^Z')
        exit_code = '148'
    os.environ['?'] = exit_code


def show_error(error):
    printf(error)


def setup_signal():
    signal(SIGINT, handle_signal)
    signal(SIGTSTP, handle_signal)
    # signal(SIGQUIT, handle_signal)


def repl_shell():
    while True:
        try:
            choice = shell.process_input()
            if choice == 'history':
                shell.print_history()
            elif choice.startswith('!'):
                try:
                    command = shell.print_history(int(choice[1:]))
                    handle_logic_op(command, isprint=True)
                except Exception:
                    printf("intek-sh: syntax error near unexpected token `newline`")
            else:
                handle_logic_op(choice, isprint=True)
        except IndexError:
            pass
        except ValueError:
            pass


def main():
    setup_terminal()
    #setup_signal()
    repl_shell()


if __name__ == "__main__":
    main()
