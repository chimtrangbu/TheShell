#!/usr/bin/env python3
import curses

def insert (source_str, insert_str, pos):
    return source_str[:pos]+insert_str+source_str[pos:]

def write_on_file(filename, content):
    with open(filename,'w') as f:
        f.write(content)

class Shell:
    HISTORY_STACK = []
    STACK_CURRENT_INDEX = 0
    PROMPT = "intek-sh$ "


    def __init__(self):
        self.window = curses.initscr()
        self.name = curses.termname()
        curses.noecho()
        self.window.keypad(True)
        self.last_cursor_pos = (0, 0)
        (self.height, self.width) =  self.window.getmaxyx()


    def	get_str(self, prompt=""):
        self.printf(prompt, end='')
        return self.window.getstr()

    def get_ch(self, prompt=""):
        pos = self.get_curs_pos()
        self.add_str(pos[0], 0 , prompt)
        return chr(self.window.getch())


    def printf(self, string="", end='\n'):
        pos = self.get_curs_pos()
        self.window.addstr(pos[0], pos[1], string+end)

    def add_str(self, y, x, string):
        self.window.addstr(y, x, string)


    def get_curs_pos(self):
        #self.window.refresh()
        pos = curses.getsyx()
        return (pos[0], pos[1])


    def set_curs_pos(self, y=None, x=None):
        self.window.refresh()
        pos = self.get_curs_pos()
        if y is None:
            y = pos[0]
        if x is None:
            x = pos[1]
        curses.setsyx(y,x)
        curses.doupdate()

    def line_count(self, string):
        """ return number of line the string can takk place based on window width """
        return int((len(string) + 10) / self.width) + 1

    def delete_nlines(self, n=1, startl=None, revese=True):
        """
        Delete n lines in curses
        - if "startl" not given: base on current curs position
        - "reverse" to delete upward (bottom to top) and so on
        """
        pos = curses.getsyx()
        if startl is None:
            self.window.move(pos[0], self.width-1)
        else:
            self.window.move(startl, self.width-1)

        for i in range(n):
            self.window.deleteln()
            if i != n-1:
                pos = curses.getsyx()
                if revese:
                    self.window.move(pos[0]-1, self.width-1)
                else:
                    self.window.move(pos[0]+1, self.width-1)




    def move_curs(self, dy, dx):
        pos = self.get_curs_pos()
        self.set_curs_pos(pos[0]+dy, pos[1]+dx)
        curses.doupdate()

    def process_KEY_UP(self, input, curs_pos):
        #global STACK_CURRENT_INDEX, HISTORY_STACK, PROMPT
        try:
            #curs_pos = curses.getsyx()

            if input not in [Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX],'\n','']:
                Shell.HISTORY_STACK.append(input)
                Shell.STACK_CURRENT_INDEX -= 1

            if abs(Shell.STACK_CURRENT_INDEX) != len(Shell.HISTORY_STACK): # Not meet the start
                self.delete_nlines(self.line_count(Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX]))
                self.window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX-1]) #print the previous
                input = Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX-1]
                Shell.STACK_CURRENT_INDEX -= 1
            else:
                if input is not Shell.HISTORY_STACK[0]: # EndOfStack
                    self.delete_nlines(self.line_count(Shell.HISTORY_STACK[0]))
                    self.window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[0])
                    input = Shell.HISTORY_STACK[0]
            return input
        except IndexError:
            pass

    def process_KEY_DOWN(self, input, curs_pos):
        #global STACK_CURRENT_INDEX, HISTORY_STACK, PROMPT
        try:
            #curs_pos = curses.getsyx()

            if input not in [Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX],'\n','']:
                Shell.HISTORY_STACK.append(input)
                Shell.STACK_CURRENT_INDEX += 1

            if Shell.STACK_CURRENT_INDEX != -1: # Not meet the end of stack
                self.delete_nlines(self.line_count(Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX]))
                self.window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX+1]) #print the previous
                input = Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX+1]
                Shell.STACK_CURRENT_INDEX += 1
            else:
                if input is not Shell.HISTORY_STACK[-1]: # EndOfStack
                    self.delete_nlines(self.line_count(Shell.HISTORY_STACK[-1]))
                    self.window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[-1])
                    input = Shell.HISTORY_STACK[-1]
            return input
        except IndexError:
            pass

    def process_input(self):
        char = self.get_ch(Shell.PROMPT)
        input = "" # inittial input

        input_pos = self.get_curs_pos()
        while char not in ['\n']:
            ######################### KEY process ########################################
            """ 
                This block's purposes are handling special KEYS 
                Add feature on this block
            """
            if char == chr(curses.KEY_UP):
                input = self.process_KEY_UP(input, input_pos)
                self.set_curs_pos(x=len(Shell.PROMPT+input))
                char = ''

            elif char == chr(curses.KEY_DOWN):
                input = self.process_KEY_DOWN(input, input_pos)
                self.set_curs_pos(x=len(Shell.PROMPT+input))
                char = ''

            elif char == chr(curses.KEY_LEFT):
                if self.get_curs_pos()[1] > 10:
                    self.move_curs(0, -1)
                char = ''

            elif char == chr(curses.KEY_RIGHT):
                if self.get_curs_pos()[1] < len(input) + 10:
                    self.move_curs(0, 1)
                char = ''

            elif ord(char) == 263: # handle BACKSPACE
                pos = self.get_curs_pos()
                del_loc = pos[0]*self.width + pos[1] - (input_pos[0]*self.width + input_pos[1])
                input = input[:del_loc-1] + input[del_loc:]
                self.delete_nlines(self.line_count(input), input_pos[0], revese=False)
                self.window.addstr(input_pos[0], 0, Shell.PROMPT + input)
                self.set_curs_pos(pos[0], pos[1]-1)
                char = ''


            ##############################################################################################
            # Insert mode
            curs_pos = self.get_curs_pos()
            if char != '':
                insert_loc = curs_pos[0]*self.width + curs_pos[1] - (input_pos[0]*self.width + input_pos[1])
                input = input[:insert_loc] + char + input[insert_loc:]
                self.window.addstr(input_pos[0], 10, input) # wrong
                self.set_curs_pos(curs_pos[0], curs_pos[1]+1)

            # loop again
            char = chr(self.window.getch())

        if input not in ['\n','']:
            Shell.HISTORY_STACK.append(input)
            Shell.STACK_CURRENT_INDEX = 0

        #set cursors
        self.window.addstr("\n")
        self.window.refresh()
        return input


def main():
    shell = Shell()

    #curses.def_shell_mode()
    while True:
        try:
            choice = shell.process_input()
            #choice = input("bash& ")
            if choice == 'exit':
                break
            else:

                """
                #curses.noecho()
                output = subprocess.check_output(choice.split()).decode()
                ls = output.split('\n')
                for l in ls:
                    window.addstr(l)
                    window.addstr('\n')
                """
                pass

        except Exception:
            pass

    curses.endwin()
main()