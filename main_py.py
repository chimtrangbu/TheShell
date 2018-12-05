#!/usr/bin/env python3
import curses
import subprocess




def insert (source_str, insert_str, pos):
    return source_str[:pos]+insert_str+source_str[pos:]

def write_file(filename, content, mode='w'):
    with open(filename, mode) as f:
        f.write(content)
        return

class Shell:
    HISTORY_STACK = []
    STACK_CURRENT_INDEX = 0
    PROMPT = "intek-sh$ "


    def __init__(self):
        self.window = curses.initscr()
        self.name = curses.termname()
        curses.noecho()
        self.window.keypad(True)
        self.window.scrollok(True)
        self.last_cursor_pos = (0, 0)
        self.write_win_file = True
        self.windowlog = 'windowlog'
        (self.height, self.width) =  self.window.getmaxyx()
        self.resize = False

    def print_history(self, index = False):
        if not index:
            for i in range(len(Shell.HISTORY_STACK)):
                self.printf("{:3d}".format(i)+'  '+str(Shell.HISTORY_STACK[i]))
        else:
            Shell.HISTORY_STACK.pop()
            Shell.STACK_CURRENT_INDEX = 0
            self.printf(Shell.HISTORY_STACK[index])


    def read_win_log(self):
        with open(self.windowlog, 'r') as f:
            data = f.read()
        if data.endswith('intek-sh$ ') or data.endswith('intek-sh$'):
            return data + ' '
        else:
            return data

    def write_win_log(self, file):
        pos = self.get_curs_pos()
        with open(self.windowlog,'w') as f:
            for i in range(pos[0]+2):
                data = self.window.instr(i,0).decode().strip()
                if data.startswith('intek-sh') and i != 0:
                    data = '\n' + data
                f.write(data)
        self.window.move(pos[0], pos[1])

    def	get_str(self, prompt=""):
        self.printf(prompt, end='')
        return self.window.getstr()

    def get_ch(self, prompt=""):
        pos = self.get_curs_pos()
        self.add_str(pos[0], 0, prompt)
        return chr(self.window.getch())

    def printf(self, string="", end='\n'):
        pos = self.get_curs_pos()
        if string.endswith('\n'):
            self.add_str(pos[0], pos[1], string)
        else:
            self.add_str(pos[0], pos[1], string+end)

    def add_str(self, y, x, string):
        self.window.addstr(y, x, string)
        self.window.refresh()

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

    def move_curs(self, dy, dx):
        pos = self.get_curs_pos()
        self.set_curs_pos(pos[0]+dy, pos[1]+dx)
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




    def process_KEY_UP(self, input, curs_pos):
        try:
            if len(Shell.HISTORY_STACK) == 0:
                return input
            if input not in [Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX],'\n','']:
                Shell.HISTORY_STACK.append(input)
                Shell.STACK_CURRENT_INDEX -= 1
            if abs(Shell.STACK_CURRENT_INDEX) != len(Shell.HISTORY_STACK): # Not meet the start
                self.delete_nlines(self.line_count(Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX]), startl=curs_pos[0], revese=False)
                #self.window.deleteln()
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
        try:
            if len(Shell.HISTORY_STACK) == 0:
                return input
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
    ##################################################################################
    def process_input(self):
        char = self.get_ch(Shell.PROMPT)
        input = "" # inittial input

        input_pos = self.get_curs_pos()
        while char not in ['\n']:
            ######################### KEY process ####################################
            """ 
                This block's purposes are handling special KEYS 
                Add feature on this block
            """
            ############# Handle window resize  ################################
            if ord(char) == 410:
                lens = len(input)
                self.window.clear()
                self.window.refresh()
                data = self.read_win_log()
                self.window.addstr(0,0,data)
                self.window.refresh()
                (self.height, self.width) =  self.window.getmaxyx()
                pos = self.get_curs_pos()
                step = pos[0]*self.width + pos[1]
                loc_step = step - lens
                input_pos = loc_step//self.width, loc_step%self.width
                #self.window.move(input_pos[0] + lens//self.width, (step + lens) % self.width)
                char = ''

            ##################################################################
            elif char == chr(curses.KEY_UP):
                input = self.process_KEY_UP(input, input_pos)
                write_file('debug',input)
                self.set_curs_pos(x=len(Shell.PROMPT+input))
                char = ''

            elif char == chr(curses.KEY_DOWN):
                input = self.process_KEY_DOWN(input, input_pos)
                self.set_curs_pos(x=len(Shell.PROMPT+input))
                char = ''

            elif char == chr(curses.KEY_LEFT):
                pos = self.get_curs_pos()
                if pos[1] > 10 or pos[0] != input_pos[0]:
                    self.move_curs(0, -1)
                elif pos[1] == 10:
                    self.set_curs_pos(pos[0], pos[1])
                char = ''

            elif char == chr(curses.KEY_RIGHT):
                pos = self.get_curs_pos()
                if pos[0]*self.width + pos[1] <= input_pos[0]*self.width + input_pos[1] + len(input) :
                    self.move_curs(0, 1)
                char = ''

            elif char == chr(127): # curses.BACKSPACE
                pos = self.get_curs_pos()
                del_loc = pos[0]*self.width + pos[1] - (input_pos[0]*self.width + input_pos[1])
                if del_loc > 0:
                    input = input[:del_loc-1] + input[del_loc:]
                self.delete_nlines(self.line_count(input), input_pos[0], revese=False)
                self.window.addstr(input_pos[0], 0, Shell.PROMPT + input)
                if pos[1] > 10 or pos[0] != input_pos[0]:
                    self.set_curs_pos(pos[0], pos[1]-1)
                elif pos[1] == 10:
                    self.set_curs_pos(pos[0], pos[1])
                char = ''

            elif ord(char) == 9: # curses.TAB
                #input = handle_completion(input,'file')
                self.window.addstr(input_pos[0], 10, input)
                char = ''

            elif char == chr(curses.KEY_DC):
                pos = self.get_curs_pos()
                del_loc = pos[0]*self.width + pos[1] - (input_pos[0]*self.width + input_pos[1]) + 1
                if del_loc > 0:
                    input = input[:del_loc-1] + input[del_loc:]
                self.delete_nlines(self.line_count(input), input_pos[0], revese=False)
                self.window.addstr(input_pos[0], 0, Shell.PROMPT + input)
                self.set_curs_pos(pos[0], pos[1])
                char = ''







            ##############################################################################################
            # Insert mode
            curs_pos = self.get_curs_pos()
            if char != '':
                insert_loc = curs_pos[0]*self.width + curs_pos[1] - (input_pos[0]*self.width + input_pos[1])
                input = input[:insert_loc] + char + input[insert_loc:]
                self.window.addstr(input_pos[0], 10, input)
                self.set_curs_pos(curs_pos[0], curs_pos[1]+1)


            # Write on window
            self.write_win_log('windowlog')
            # loop again
            char = chr(self.window.getch())

        if input not in ['\n','']:
            Shell.HISTORY_STACK.append(input)
            Shell.STACK_CURRENT_INDEX = 0

        # Write the PROMPT tp file when press Enter with APPEND mode
        write_file(self.windowlog, '\n'+Shell.PROMPT, mode = 'a')

        # Refresh the window and enter newline
        self.window.addstr("\n")
        self.window.refresh()
        return input


def main():
    shell = Shell()

    while True:
        try:
            choice = shell.process_input()
            if choice == 'history':
                shell.print_history()

            elif choice.startswith('!'):
                try:
                    shell.print_history(int(choice[1:]))
                except Exception:
                    shell.printf("intek-sh: syntax error near unexpected token `newline`")

            elif choice == 'print':
                shell.printf("hello")
            else:
                pass
                """
                try:
                    #curses.noecho()
                    output = subprocess.check_output(choice.split()).decode()
                    shell.printf(output)
                except Exception:
                    pass
                """
        except Exception:
            pass
    curses.endwin()
main()