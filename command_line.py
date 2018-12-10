import curses
from completion import handle_completion, get_suggest


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
        global window
        window = curses.initscr()
        self.name = curses.termname()
        curses.noecho()
        window.keypad(True)
        window.scrollok(True)
        self.last_cursor_pos = (0, 0)
        self.write_win_file = True
        self.windowlog = 'windowlog'
        self.height, self.width =  window.getmaxyx()
        self.preivous_key = ""
        self._get_history()
    def _get_history(self):
        open('history', 'a').close()
        with open('history', 'r') as f:
            for line in f:
                Shell.HISTORY_STACK.append(line.strip())
    def write_history_file(self):
        write_file('history',"\n".join(Shell.HISTORY_STACK),'a')

    def print_history(self, index = False):
        if not index:
            for i in range(len(Shell.HISTORY_STACK)):
                self.printf("{:3d}".format(i)+'  '+str(Shell.HISTORY_STACK[i]))
        else:
            Shell.HISTORY_STACK.pop()
            Shell.STACK_CURRENT_INDEX = 0
            self.printf(Shell.HISTORY_STACK[index])
            return Shell.HISTORY_STACK[index]


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
            s = ''
            for i in range(pos[0]+2):
                data = window.instr(i,0).decode().strip(' ')
                if len(data) < self.width:
                    s += data + '\n'
                else:
                    s += data
            f.write(s.strip('\n'))
        window.move(pos[0], pos[1])

    def	get_str(self, prompt=""):
        self.printf(prompt, end='')
        return window.getstr()

    def get_ch(self, prompt=""):
        pos = self.get_curs_pos()
        self.add_str(pos[0], 0, prompt)
        return chr(window.getch())

    def printf(self, string="", end='\n'):
        pos = self.get_curs_pos()
        if string.endswith('\n'):
            self.add_str(pos[0], pos[1], string)
        else:
            self.add_str(pos[0], pos[1], string+end)
        write_file(self.windowlog, string+'\n','a')

    def add_str(self, y, x, string):
        window.addstr(y, x, string)
        window.refresh()

    def get_curs_pos(self):
        #window.refresh()
        pos = curses.getsyx()
        return (pos[0], pos[1])

    def set_curs_pos(self, y=None, x=None):
        window.refresh()
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
            window.move(pos[0], self.width-1)
        else:
            window.move(startl, self.width-1)

        for i in range(n):
            window.deleteln()
            if i != n-1:
                pos = curses.getsyx()
                if revese:
                    window.move(pos[0]-1, self.width-1)
                else:
                    window.move(pos[0]+1, self.width-1)


    def _process_KEY_UP(self, input, curs_pos):
        try:
            if len(Shell.HISTORY_STACK) == 0:
                return input
            if input not in [Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX],'\n','']:
                Shell.HISTORY_STACK.append(input)
                Shell.STACK_CURRENT_INDEX -= 1
            if abs(Shell.STACK_CURRENT_INDEX) != len(Shell.HISTORY_STACK): # Not meet the start
                self.delete_nlines(self.line_count(Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX]), startl=curs_pos[0], revese=False)
                #window.deleteln()
                window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX-1]) #print the previous
                input = Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX-1]
                Shell.STACK_CURRENT_INDEX -= 1
            else:
                if input is not Shell.HISTORY_STACK[0]: # EndOfStack
                    self.delete_nlines(self.line_count(Shell.HISTORY_STACK[0]))
                    window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[0])
                    input = Shell.HISTORY_STACK[0]
            return input
        except IndexError:
            pass

    def _process_KEY_DOWN(self, input, curs_pos):
        try:
            if len(Shell.HISTORY_STACK) == 0:
                return input
            if input not in [Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX],'\n','']:
                Shell.HISTORY_STACK.append(input)
                Shell.STACK_CURRENT_INDEX += 1
            if Shell.STACK_CURRENT_INDEX != -1: # Not meet the end of stack
                self.delete_nlines(self.line_count(Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX]))
                window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX+1]) #print the previous
                input = Shell.HISTORY_STACK[Shell.STACK_CURRENT_INDEX+1]
                Shell.STACK_CURRENT_INDEX += 1
            else:
                if input is not Shell.HISTORY_STACK[-1]: # EndOfStack
                    self.delete_nlines(self.line_count(Shell.HISTORY_STACK[-1]))
                    window.addstr(curs_pos[0], 0, Shell.PROMPT + Shell.HISTORY_STACK[-1])
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
                window.clear()
                window.refresh()
                data = self.read_win_log()
                window.addstr(0,0,data)
                window.refresh()
                (self.height, self.width) =  window.getmaxyx()
                pos = self.get_curs_pos()
                step = pos[0]*self.width + pos[1]
                loc_step = step - lens
                input_pos = loc_step//self.width, loc_step%self.width
                #window.move(input_pos[0] + lens//self.width, (step + lens) % self.width)
                char = ''

            ##################################################################
            elif char == chr(curses.KEY_UP):
                self.preivous_key = ''
                input = self._process_KEY_UP(input, input_pos)
                self.set_curs_pos(x=len(Shell.PROMPT+input))
                char = ''

            elif char == chr(curses.KEY_DOWN):
                self.preivous_key = ''
                input = self._process_KEY_DOWN(input, input_pos)
                self.set_curs_pos(x=len(Shell.PROMPT+input))
                char = ''

            elif char == chr(curses.KEY_LEFT):
                self.preivous_key = ''
                pos = self.get_curs_pos()
                if pos[1] > 10 or pos[0] != input_pos[0]:
                    if pos[1] - 1 < 0:
                        pos = (pos[0] - 1, self.width)
                    self.set_curs_pos(pos[0], pos[1]-1)
                elif pos[1] == 10:
                    self.set_curs_pos(pos[0], pos[1])
                char = ''

            elif char == chr(curses.KEY_RIGHT):
                self.preivous_key = ''
                pos = self.get_curs_pos()
                step = pos[0]*self.width + pos[1] + 1
                if step <= input_pos[0]*self.width + input_pos[1] + len(input):
                    self.set_curs_pos(step // self.width, step % self.width)
                char = ''

            elif char == chr(127): # curses.BACKSPACE
                self.preivous_key = ''
                pos = self.get_curs_pos()
                del_loc = pos[0]*self.width + pos[1] - (input_pos[0]*self.width + input_pos[1])
                if del_loc > 0:
                    input = input[:del_loc-1] + input[del_loc:]
                self.delete_nlines(self.line_count(input), input_pos[0], revese=False)
                window.addstr(input_pos[0], 0, Shell.PROMPT + input)
                if pos[1] > 10 or pos[0] != input_pos[0]:
                    self.set_curs_pos(pos[0], pos[1]-1)
                elif pos[1] == 10:
                    self.set_curs_pos(pos[0], pos[1])
                char = ''

            elif ord(char) == 9: # curses.TAB
                if self.preivous_key in ['TAB','TAB2']: # second TAB
                    data = ''
                    if input.endswith(' '):
                        data = "\n".join(get_suggest("", 'file'))
                    else:
                        data = "\n".join(get_suggest(input.strip(), 'command'))
                    if len(data):
                        self.printf('\n'+data)
                        self.preivous_key = 'TAB2'
                        break
                else:
                    if input != handle_completion(input, 'command'):
                        input = handle_completion(input, 'command')
                    self.preivous_key = 'TAB'

                window.addstr(input_pos[0], 10, input)
                window.refresh()
                char = ''
            elif char == chr(curses.KEY_DC):
                self.preivous_key = ''
                pos = self.get_curs_pos()
                del_loc = pos[0]*self.width + pos[1] - (input_pos[0]*self.width + input_pos[1]) + 1
                if del_loc > 0:
                    input = input[:del_loc-1] + input[del_loc:]
                self.delete_nlines(self.line_count(input), input_pos[0], revese=False)
                window.addstr(input_pos[0], 0, Shell.PROMPT + input)
                self.set_curs_pos(pos[0], pos[1])
                char = ''







            ##############################################################################################
            # Insert mode
            curs_pos = self.get_curs_pos()
            if char != '':
                self.preivous_key = char
                insert_loc = curs_pos[0]*self.width + curs_pos[1] - (input_pos[0]*self.width + input_pos[1])
                input = input[:insert_loc] + char + input[insert_loc:]
                window.addstr(input_pos[0], 10, input)
                self.set_curs_pos(curs_pos[0], curs_pos[1]+1)

            # Write on window
            self.write_win_log('windowlog')
            # loop again
            char = chr(window.getch())


        if self.preivous_key not in['TAB2'] :
            step = input_pos[0]*self.width + input_pos[1] + len(input)
            window.move(step // self.width, step % self.width)

        if input not in ['\n','']:
            Shell.HISTORY_STACK.append(input)
            Shell.STACK_CURRENT_INDEX = 0

        # Write the PROMPT tp file when press Enter with APPEND mode
        write_file(self.windowlog, '\n'+Shell.PROMPT, mode = 'a')
        # Refresh the window and enter newline
        if self.preivous_key in ['TAB2']:
            char = self.get_ch(Shell.PROMPT)
            input = ""  
        else:
            window.addstr("\n")
        window.refresh()
        return input