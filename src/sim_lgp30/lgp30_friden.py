from sim_lgp30.friden_constants import * # for Friden Flexowriter constants

from sim_lgp30.simulator_constants import * # for the exception classes

from pathlib import Path # for Path

import sim_lgp30. console_nonblock as console

import time # for time.time() and time.sleep()

class Friden():

    def start_reader(self, friden_code):
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")

    def stop_reader(self, friden_code):
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")
    
    def to_upper_case(self, friden_code):
        self.case = CASE_UPPER
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")
    
    def to_lower_case(self, friden_code):
        self.case = CASE_LOWER
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")
    
    def toggle_colour(self, friden_code):
        self.colour = not self.colour
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")
        else:
            if self.colour is COLOUR_BLACK:
                console.put_string('\n<blk>'if not ANSI_TERMINAL else ANSI_BLACK, end = '')
            else:
                console.put_string('\n<red>' if not ANSI_TERMINAL else ANSI_RED, end = '')

    def print_unused(self, friden_code):
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")
        else:
            # nothing to print
            pass

    def print_character(self, friden_code):
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")
        else:
            python_char = self.OUTPUT_CODESET[friden_code][self.case]
            console.put_string(python_char, end = '')
            self.platten_pos += 1
    
    def print_backspace(self, friden_code):
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")
        else:
            # perhaps the console can do something with this
            python_char = self.OUTPUT_CODESET[friden_code][self.case]
            console.put_string(python_char, end = '')
            self.platten_pos -= 1
    
    def print_crlf(self, friden_code):
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")
        else:
            console.put_string('\n', end='')
            self.platten_pos = 1

    def write_tab_stops(self, tab_stop_list):
        self.tab_stops = tab_stop_list

    def read_tab_stops(self):
        return self.tab_stops
        
    def print_tab(self, friden_code):
        if (self.cpu.run_mode == RUN_MODE_STEP) or (self.cpu.run_mode == RUN_MODE_TRACE):
            python_desc = self.OUTPUT_CODESET[friden_code][self.CHAR_DESC]
            console.put_string(f"To printer: {python_desc}")   
        else:
            for index in range(len(self.tab_stops)):
                spaces_to_print = self.tab_stops[index] - self.platten_pos
                if spaces_to_print > 0:
                    console.put_string(' '*spaces_to_print, end = '')
                    self.platten_pos = self.tab_stops[index]
                    break

    def __init__(self, cpu):
        self.cpu = cpu
        self.pathname = ''
        self.input_source = FRIDEN_SOURCE_KB
        self.file = None
        self.case = DEFAULT_CASE
        self.colour = DEFAULT_COLOUR
        self.mode = FRIDEN_DEFAULT_MODE
        self.tab_stops = []
        self.platten_pos = 1
        self.INPUT_CHARSET = {
            # {character:code}
            '\t':24,
            ' ':3,
            '"':14,
            '$':26,
            '%':22,
            "'":32,
            '(':38,
            ')':2,
            '*':10,
            '+':11,
            ',':27,
            '-':7,
            '.':23,
            '/':19,
            '0':2,
            '1':6,
            '2':10,
            '3':14,
            '4':18,
            '5':22,
            '6':26,
            '7':30,
            '8':34,
            '9':38,
            ':':15,
            ';':15,
            '=':11,
            '?':19,
            'A':57,
            'B':5,
            'C':53,
            'D':21,
            'E':37,
            'F':42,
            'G':46,
            'H':49,
            'I':17,
            'J':50,
            'K':54,
            'L':6,
            'M':29,
            'N':25,
            'O':35,
            'P':33,
            'Q':58,
            'R':13,
            'S':61,
            'T':45,
            'U':41,
            'V':31,
            'W':62,
            'X':39,
            'Y':9,
            'Z':1,
            '[':27,
            ']':23,
            '_':7,
            'a':57,
            'b':5,
            'c':53,
            'd':21,
            'e':37,
            'f':42,
            'g':46,
            'h':49,
            'i':17,
            'j':50,
            'k':54,
            'l':6,
            'm':29,
            'n':25,
            'o':35,
            'p':33,
            'q':58,
            'r':13,
            's':61,
            't':45,
            'u':41,
            'v':31,
            'w':62,
            'x':39,
            'y':9,
            'z':1,
            'Δ':18,
            'Σ':34,
            '∏':30
            }
        # indices into output lookup tuple
        self.CHAR_DESC = 0
        self.CHAR_UCASE = 1
        self.CHAR_LCASE = 2
        self.CHAR_HANDLER = 3
        # {code: tuple}
        self.OUTPUT_CODESET = {
            # key is track number
            0:('start','','',self.start_reader),
            1:('Z z','Z','z',self.print_character),
            2:(') 0',')','0',self.print_character),
            3:('space',' ',' ',self.print_character),
            4:('lower','','',self.to_lower_case),
            5:('B b','B','b',self.print_character),
            6:('L l 1','L','l',self.print_character),
            7:('_ -','_','-',self.print_character),
            8:('upper','','',self.to_upper_case),
            9:('Y y','Y','y',self.print_character),
            10:('* 2','*','2',self.print_character),
            11:('= +','=','+',self.print_character),
            12:('colour','','',self.toggle_colour),
            13:('R r','R','r',self.print_character),
            14:('" 3','"','3',self.print_character),
            15:(': ;',':',';',self.print_character),
            16:('return','','',self.print_crlf),
            17:('I i','I','i',self.print_character),
            18:('Δ 4','Δ','4',self.print_character),
            19:('? /','?','/',self.print_character),
            20:('backsp','\b','\b',self.print_backspace),
            21:('D d','D','d',self.print_character),
            22:('% 5','%','5',self.print_character),
            23:('] .',']','.',self.print_character),
            24:('tab','','',self.print_tab),
            25:('N n','N','n',self.print_character),
            26:('$ 6','$','6',self.print_character),
            27:('[ '+',','[',',',self.print_character),
            28:('unused','','',self.print_unused),
            29:('M m','M','m',self.print_character),
            30:('∏ 7','∏','7',self.print_character),
            31:('V v','V','v',self.print_character),
            32:('stop','','',self.stop_reader),
            33:('P p','P','p',self.print_character),
            34:('Σ 8','Σ','8',self.print_character),
            35:('O o','O','o',self.print_character),
            36:('unused','','',self.print_unused),
            37:('E e','E','e',self.print_character),
            38:('( 9','(','9',self.print_character),
            39:('X x','X','x',self.print_character),
            40:('unused','','',self.print_unused),
            41:('U u','U','u',self.print_character),
            42:('F f','F','f',self.print_character),
            43:('unused','','',self.print_unused),
            44:('unused','','',self.print_unused),
            45:('T t','T','t',self.print_character),
            46:('G g','G','g',self.print_character),
            47:('unused','','',self.print_unused),
            48:('unused','','',self.print_unused),
            49:('H h','H','h',self.print_character),
            50:('J j','J','j',self.print_character),
            51:('unused','','',self.print_unused),
            52:('unused','','',self.print_unused),
            53:('C c','C','c',self.print_character),
            54:('K k','K','k',self.print_character),
            55:('unused','','',self.print_unused),
            56:('unused','','',self.print_unused),
            57:('A a','A','a',self.print_character),
            58:('Q q','Q','q',self.print_character),
            59:('unused','','',self.print_unused),
            60:('unused','','',self.print_unused),
            61:('S s','S','s',self.print_character),
            62:('W w','W','w',self.print_character),
            63:('delete','','',self.print_unused)
            }

    def six2four_bits(self, six_bit_code):
        return(six_bit_code >> 2)
    
    def set_input_source(self, source):
        self.input_source = source

    def set_mode(self, mode):
        self.mode = mode

    def open(self, pathname):
        self.pathname = pathname
        path = Path(pathname)
        if path.is_file():
            self.file = path.open(mode='r', encoding ='ascii')
            return
        else:
            self.pathnme = ''
            self.file = None
            raise IOError(f"Invalid pathname: {pathname}")
        
    def close_file(self):
        if self.file is not None:        
            self.file.close()
            self.pathname = ''
            self.file = None

    def get_kb_code(self):
        if console.char_available():
            in_char = console.get_char()
            if (in_char == '\n') or (in_char == '\r'):
                self.put_code(CHAR_CRLF)
                return None
            if in_char not in self.INPUT_CHARSET:
                raise IllegalCharacterError(f"Illegal character from keybord: {in_char}")
            in_code = self.INPUT_CHARSET[in_char]
            # special case - return the stop code
            if in_code == CHAR_STOP:
                return in_code
            if self.mode == FRIDEN_MODE_4BIT:
                return self.six2four_bits(in_code)
            else:
                return in_code
        else:
            return None

    def get_tape_code(self):
        if self.file is not None:
            in_char = self.file.read(1)
            if in_char != '':
                if (in_char == '\n') or (in_char == '\r'):
                    self.put_code(CHAR_PERIOD)
                    self.put_code(CHAR_CRLF)
                    return None
                if in_char not in self.INPUT_CHARSET:
                    raise IllegalCharacterError(f"Illegal character from tape file: {in_char}")
                in_code = self.INPUT_CHARSET[in_char]
                # special case - return the stop code
                if in_code == CHAR_STOP:
                    return in_code
                if self.mode == FRIDEN_MODE_4BIT:
                    return self.six2four_bits(in_code)
                else:
                    return in_code
            else:
                self.close_file()
                raise EOFError('End of tape file')
        else:
            raise IOError('No tape file')

    def get_code(self):
        if self.input_source == FRIDEN_SOURCE_KB:
            return(self.get_kb_code())
        else: # self.input_source = FRIDEN_SOURCE_TAPE
            return(self.get_tape_code())
    
    def await_code(self):
        # The simulator will not wait forever for input
        start_time = time.time()
        while True:
            # The following will raise (not handled here):
            # IllegalCharacterError for non-Friden code
            # EOFError for end of tape file
            code = self.get_code()
            if code is not None:
                return code
            else:
                # don't hog the CPU
                time.sleep(FRIDEN_SLEEP_INTERVAL)
                if time.time() - start_time > FRIDEN_TIMEOUT:
                    raise InputTimeoutError('Timed out waiting for input')

    def put_code(self, code):
        handler = self.OUTPUT_CODESET[code][self.CHAR_HANDLER]
        handler(code)
