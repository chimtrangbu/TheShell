#!/usr/bin/env python3
from parse_command_shell import Token

operators = ['>', '>>', '<']
def redirections(string):
    return Token(string).split_token()

print(redirections('cat history|tail |>>d'))