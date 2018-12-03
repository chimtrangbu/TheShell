import os


def get_all_commands():
    '''
    Task: + Get all command from path environment
    '''
    commands = []
    for path in os.environ['PATH'].split(':'):
        if os.path.exists(path):
            commands += os.listdir(path)
    return commands


def get_all_files(path):
    '''
    Task: + Get all file or
    where_am_i
    count_double_agents
    find_password
    find_traitor
    find_info
    what_is_your_20
    intruders
    correction
    FFFFFFF

    Failures:

      1) should work with only different ip before 05

           expected: "1 34.92.5.177\n1 64.94.3.200\n1 70.15.6.236\n1 99.84.4.194\n1 129.159.8.168\n1 148.30.2.34\n1 181.20.1.154\n1 186.65.9.187\n1 213.240.7.248\n1 236directory at head of path passed
    '''
    head, _ = os.path.split(path)
    if head:
        return [os.path.join(head, p)  for p in os.listdir(head)]
    return os.listdir('.')


def get_suggest(txt, mode):
    '''
    Task: + Find all suggest from text passed at the mode
          + One is command
          + Two is file or directory at that directory
    '''
    if mode is 'command':
        valids = get_all_commands()
    else:
        valids = get_all_files(txt)
    
    suggests = [i for i in valids if i.lower().startswith(txt)]
    return suggests


def is_possible_completion(suggests, text):
    '''
    Task: + That is any suggest same text passed
    Return: Boolean
    '''
    return min(suggests, key=lambda o: len(o)) != text


def find_common_suggest(suggests, txt):
    '''
    Task: + Let max length command is key
          + Increase index from length of text passed
          + If some suggest not same then return right away
    '''
    index = len(txt)
    max_command = max(suggests).lower()
    while index < len(max_command):
        for e in suggests:
            if not e.lower().startswith(max_command[:index + 1]):
                return max_command[: index]
        index += 1
    return txt


def handle_completion(text, mode):
    '''
    Tasks: + Find all suggest from text passed at that mode
           + Find common from that list of suggest
           + Then return it
    '''
    list_suggest = get_suggest(text, mode=mode)
    if len(list_suggest) is 1:
        return list_suggest[0]
    elif list_suggest and is_possible_completion(list_suggest, text):
        return find_common_suggest(list_suggest, text)
    return text


if __name__ == '__main__':
    print(handle_completion('pyt', mode='command'))