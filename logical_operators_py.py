from os import environ
from shlex import split as split_args
from parse_command_posix import Token
from shell import run_process


def handle_logic_op(string, *, output=True):
    '''
    Tasks: + First get step need to do from parse command operator
           + Run command and if exit status isn't 0 and operator is 'and' then skip
           + else exit status is 0 and operator is 'or' then skip
    '''
    steps_exec = _parse_command_operator(string)
    # print(steps_exec)
    operator = ''
    data = []
    for i, step in enumerate(steps_exec):
        command = step[0]
        op = step[1]
        if _is_skip_command(i, operator) and _is_boolean_command(command[0]):
            command = handle_com_substitution(command)
            # run command with arguments
            result = run_process(command, output=output)
            if result:
                data += result
        operator = op
    return data


def handle_com_substitution(arguments):
    new_command = []
    for arg in arguments:
        if arg.startswith('`') and arg.endswith('`'):
            arg = Token(arg[1:-1:]).split_token()
            result = handle_logic_op(arg, output=False)
            if result:
                new_command += result
        else:
            new_command.append(arg)
    return new_command


def _is_skip_command(index, operator):
    if operator == '&&':
        return index == 0 or environ['?'] == '0'
    return index == 0 or environ['?'] != '0'


def _is_boolean_command(command):
    if command == 'false':
        environ['?'] = '1'
    elif command == 'true':
        environ['?'] = '0'
    else:
        return True
    return False


def _parse_command_operator(string):
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


if __name__ == "__main__":
    handle_logic_op('false || echo "hhaha" && ls -la && echo How i this shit')
    # print(_parse_command_operator("fasle || echo 'hhaha'"))
    # print(handle_logic_op('ls &&ls&&ls&&ls||echo "dawdaw"'))
    # handle_logic_op('ls ||ls&&ls||ls&&echo "dawdaw"')
    # handle_logic_op('ls ||ls&&ls||ls&&echo "dawdaw"||   echo "dawdawdawdaw" && echo "shekcon"')