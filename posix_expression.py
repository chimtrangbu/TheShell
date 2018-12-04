import shlex

from logical_operators import handle_logic_op
from parse_command_posix import Token

def main():
    # st = " echo \" hello world\" \" haha\"|| haha||echo 'hello world' `hahaha leuleu`"
    # st = "echo haha&&echo leu leu "
    # st = "echo `haha leu leu`||echo hello world&&echo shekcon"
    st = 'false ||echo `echo shekcon leuleu && ls` "hhaha" && ls -la && echo "How i this shit"'
    # input_user = input("intek-sh$ ")
    args = Token(st).split_token()
    handle_logic_op(args)


if __name__ == '__main__':
    main()
