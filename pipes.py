#!/usr/bin/env python3
import re

# operators = ['>', '>>', '<', '|']
# def pipes(string):
#     n = len(string) - 1
#     chars = list(string)
#     args = []
#     while n:
#         if chars[n] is ' ' or chars[n] in operators:
#             if n < len(chars) - 1:
#                 args.append(''.join(chars[n+1:]))
#             if chars[n] is not ' ':
#                 args.append(chars[n])
#             chars = chars[:n]
#         n -= 1
#     args.reverse()
#
#     return args


regex = r'(?<!\|)\|(?!\|)'
pipes = re.split(regex, 'cho bxk||g|hl>gyej$')
# print(pipes('echo a | grep z> 5>>as>d| s a'))
print(pipes)
