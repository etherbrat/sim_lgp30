# Tidy up primary bootstrap and test/debug the bootstrap process
# Check command line inputs
# Repeat all tests
# Check output
# Try the floating point interpretive system
# Implement v-loader export (?)

import sys # for sys.exit()

import os # for os.chdir()

import subprocess # for subprocess.run()

import argparse # for command line arguments

from pathlib import Path # for file pathname dissection

import itertools # for zip_longest()

from functools import reduce # used for switch list to bitmask

from operator import or_ # used for switch list to bitmask

import time # for time.sleep()

import sim_lgp30.console_nonblock as console

from sim_lgp30.simulator_constants import *
from sim_lgp30.lgp30_dissect import addr2track, addr2sector, disassemble_instr, render_disassembly, show_address
from sim_lgp30.lgp30_cpu import LGP30_CPU
from sim_lgp30.friden_constants import FRIDEN_MODE_4BIT, FRIDEN_MODE_6BIT, FRIDEN_SOURCE_KB, FRIDEN_SOURCE_TAPE, ANSI_TERMINAL
from sim_lgp30.lgp30_atq import atq2python, eatq2python, python2atq
from sim_lgp30.lgp30_hexfile_loader import HexfileLoader
from sim_lgp30.lgp30_tape_loader import TapeLoader

# This could be a logger if one was so inclined
def debug_log(a_string):
    if DEBUG:
        console.put_string(a_string)

def print_splash():
    if ANSI_TERMINAL:
        columns, lines = os.get_terminal_size()
        console.put_string("\033[30;47m\033[2J\033[H") # black text, white background
        total_spaces = " " * (columns * lines)
        console.put_string(f"\033[H{total_spaces}\033[H")
    console.put_string(f"SIM_LGP30 version {SIM_LGP30_VERSION}")

def print_help():
    console.put_string('Commands:')
    for command in commands:
        console.put_string(f"{command} - {commands[command][CMDTBL_HELP_TEXT_INDEX]}")
    console.put_string('Minimal command abbreviations are accepted')
    console.put_string('Addresses must be positive')
    console.put_string('')
    
def validate_lgp30_address(addr_str):
    debug_log(f"Validating LGP-30 address: {addr_str}")
    addr_value = evaluate_integer_string(addr_str)
    if addr_value is not None:
        if LGP30_MIN_ADDR <= addr_value <= LGP30_MAX_ADDR:
            debug_log(f"Address: {addr_value}")
            return addr_value
        else:
            debug_log(f"Address: {addr_value} out of range")
            return None
    else:
        debug_log(f"Invalid integer representation: {addr_str}")
        return None

def evaluate_integer_string(value_str):
    debug_log(f"Evaluating integer string: {value_str}")
    try:
        value = int(value_str, base=0)
        return value
    except:
        return None    

def validate_lgp30_integer(value_str):
    debug_log(f"Validating LGP-30 integer: {value_str}")
    value = evaluate_integer_string(value_str)
    if value is not None:
        if LGP30_MIN_INT <= value <= LGP30_MAX_INT:
            debug_log(f"Value: {value}")
            return value
        else:
            debug_log(f"Value: {value} out of range")
            return None
    else:
        debug_log(f"Invalid integer representation: {value_str}")
        return None

def validate_lgp30_track_sector(ts_string):
    debug_log(f"Validating LGP-30 track sector: {ts_string}")
    if len(ts_string) == LGP30_NUM_TRACK_SECTOR_DIGITS:
        track_digits = ts_string[0:2]
        sector_digits = ts_string[2:4]
        debug_log(f"Track digits: {track_digits}; Sector_digits: {sector_digits}")
        track_num = evaluate_integer_string((track_digits.lstrip('0') or '0')) # keep one zero
        sector_num = evaluate_integer_string((sector_digits.lstrip('0') or '0')) # keep one zero
        debug_log(f"Track: {track_num}, Sector: {sector_num}")
        if (track_num is not None) and \
           (sector_num is not None) and \
           0 <= track_num < LGP30_NUM_TRACKS and \
           0 <= sector_num < LGP30_SECTORS_PER_TRACK:
            address = track_num * LGP30_SECTORS_PER_TRACK + sector_num
            debug_log(f"Address: {address}")
            return address
        else:
            debug_log(f"Invalid track/sector representation: {ts_string}")
            return None            
    else:
        debug_log(f"Invalid track/sector representation: {ts_string}")
        return None            

def validate_switch(switch_str):
    debug_log(f"Validating switch {switch_str}")
    if switch_str in ['32', '16', '8', '4', '0']:
        return int(switch_str)
    else:
        return None

def validate_path2dir(path_str):
    debug_log(f"Validating path: {path_str}")
    path_obj = Path(path_str)
    if path_obj.is_dir():
        return(path_str)
    else:
        return None

def validate_path4filewrite(path_str):
    debug_log(f"Validating path: {path_str}")
    path_obj = Path(path_str)
    if path_obj.is_file():
        debug_log(f"Overwriting existing file: {path_obj.name}")
        return path_str
    else:
        if path_obj.parent.exists():
            debug_log(f"Creating new file: {path_obj.name}")
            return path_str
        else:
            return None
        return None

def validate_path4fileread(path_str):
    if path_str == '0':
        return path_str
    debug_log(f"Validating path: {path_str}")
    path_obj = Path(path_str)
    if path_obj.is_file():
        debug_log('File exists')
        return path_str
    else:
        debug_log('No such file')
        return None

def validate_qvalue(qvalue_str):
    debug_log(f"Validating qvalue: {qvalue_str}")
    try:
        qvalue = int(qvalue_str)
        if LGP30_MIN_QVALUE <= qvalue <= LGP30_MAX_QVALUE:
            return qvalue
        else:
            debug_log('Invalid qvalue')
            return None
    except:
        debug_log('Invalid qvalue string')
        return None

def validate_eqvalue(eqvalue_str):
    debug_log(f"Validating qvalue: {eqvalue_str}")
    try:
        eqvalue = int(eqvalue_str)
        if LGP30_MIN_EQVALUE <= eqvalue <= LGP30_MAX_EQVALUE:
            return eqvalue
        else:
            debug_log('Invalid extended qvalue')
            return None
    except:
        debug_log('Invalid extended qvalue string')
        return None

def validate_tab_stop(tab_stop_str):
    debug_log(f"Validating tab_stop: {tab_stop_str}")
    try:
        tab_stop = int(tab_stop_str)
        if 0 <= tab_stop <= MAX_TAB_STOP:
            return tab_stop
        else:
            debug_log('Invalid tab stop')
            return None
    except:
        debug_log('Invalid tab stop')
        return None

def validate_tapemode(mode_str):
    debug_log(f"Validating tape mode: {mode_str}")
    if mode_str in ['4', '6']:
        return mode_str
    else:
        return None

def validate_integer(integer_str):
    debug_log(f"Validating integer: {integer_str}")
    try:
        value = int(integer_str)
        return value
    except:
        debug_log('Invalid integer string')
        return None

def validate_value(value_str):
    debug_log(f"Validating value: {value_str}")
    try:
        value = float(value_str)
        return value
    except:
        debug_log('Invalid value string')
        return None

def validate_onoff(mode_str):
    debug_log(f"Validating On/Off mode: {mode_str}")
    if mode_str in ['on', 'off']:
        return mode_str
    else:
        return None

def validate_input_source(source_str):
    if source_str in ['kb', 'tape']:
        return source_str
    else:
        return None

def validate_no_args(element):
    # Args:
    # 0: Target directory
    return True

def accumulator_init_command(arg_list):
    # Args:
    # 0 (optional): Value to write to A/ac
    if len(arg_list) == 1:
        cpu.ac.write(arg_list[0])
    ac_string = f"A/ac"
    data = cpu.ac.read()
    d = disassemble_instr(data)
    data_string = f"{render_disassembly(d)}"
    console.put_string(f"{ac_string}: {data_string}")
    return True            

def atqdeposit_command(arg_list):
    # Args:
    # 0: Address
    # 1: Value
    # 2: Qvalue
    try:
        address = arg_list[0]
        q_value = arg_list[2]
        value = python2atq(arg_list[1], q_value)      
        cpu.mem.write(address, value)
        console.put_string(f"{address}: {atq2python(cpu.mem.read(address), q_value)} {q_value}")
        return True
    except:
        console.put_string(f"Invalid value {arg_list[1]} at q = {arg_list[2]}")
        return False

def atqexamine_command(arg_list):
    # Args:
    # 0: Address
    # 1: Qvalue
    address = arg_list[0]
    q_value = arg_list[1]
    data = cpu.mem.read(address)
    if data is not None:
        console.put_string(f"{address}: {atq2python(cpu.mem.read(address), q_value)} {q_value}")
    else:
        console.put_string(f"{address}: No data")
    return True

def blackjack_command(arg_list):
    # Args:
    # 0 (optional): Blackjack mode
    if len(arg_list) == 1:
        if arg_list[0] == 'on':
            cpu.blackjack_mode = True
        else:
            cpu.blackjack_mode = False
    if cpu.blackjack_mode:
        console.put_string('Blackjack mode: On')
    else:
        console.put_string('Blackjack mode: Off')
    return True

def cd_command(arg_list):
    # Args:
    # 0: Target directory
    os.chdir(arg_list[0])
    pwd_command([])
    return True

def convert_command(arg_list):
    # Args:
    # 0: Converted TTSS value
    console.put_string(f"{arg_list[0]}")
    return True

def deposit_command(arg_list):
    # Args:
    # 0: Address
    # 1: Data
    address = arg_list[0]
    data = arg_list[1]
    cpu.mem.write(address, data)
    data = cpu.mem.read(address)
    show_address(address, data)
    return True

def dir_command(arg_list):
    # Args:
    # None
    current_dir = Path.cwd()
    files = [item.name for item in current_dir.iterdir() if item.is_file()]
    for file in files:
        console.put_string(file)
    return True

def eatqexamine_command(arg_list):
    # Args:
    # 0: Address
    # 1: Qvalue
    # Assume that the result of m multiply has been saved at address
    # and the result of n multiply is in the accumulator
    address = arg_list[0]
    q_value = arg_list[1]
    high_part = cpu.mem.read(arg_list[0])
    low_part = cpu.ac.read()
    if (high_part is not None) and (low_part is not None):
        # eatq2python takes an un-offset, 62-bit two's compliment binary value 
        # shift the low part right to get rid of the spacer bit, leaving 31 bits
        # shift the high part right to get rid of the spacer bit, then left 31 bits
        # to position it above th low part - effectively a 30-bit left shift
        # console.put_string(f"{high_part:032b}, {low_part:032b}")
        data = (high_part << 30) + (low_part >> 1)
        console.put_string(f"{address}: {eatq2python(data, q_value)} {q_value}")
    else:
        console.put_string(f"{address}: No data in high part and/or low part")
    return True

def examine_command(arg_list):
    # Args:
    # 0: <range start>
    # [1: <range end>]
    range_start = arg_list[0]
    if len(arg_list) == 1:
        data = cpu.mem.read(range_start)
        show_address(range_start, data)
        return True
    else:
        range_end = arg_list[1]
        if range_end >= range_start:
            for address in range (range_start, range_end + 1):
                data = cpu.mem.read(address)
                show_address(address, data)
            return True
        else:
            console.put_string("Ascending address range required")
            return False

def exit_command(arg_list):
    # Args:
    # (none)
    sys.exit(0)

def drum2hex_command(arg_list):
    # Args:
    # 0: Pathname of Intel hex file to be written from memory
    debug_log(f"Writing hex file: {arg_list[0]}")
    hexfile_loader.mem_to_hexfile(arg_list[0], cpu.start_address)
    return True
    
def hex2drum_command(arg_list):
    # Args:
    # 0: Pathname of Intel hex file to be read into memory
    console.put_string(f"Reading hex file: {arg_list[0]}")
    try:
        hexfile_start_address = hexfile_loader.hexfile_to_mem(arg_list[0])
        if hexfile_start_address is not None:
            console.put_string(f"Start address in hex file: {hexfile_start_address}")
            cpu.start_address = hexfile_start_address
            cpu.pc.write(hexfile_start_address)
            cpu.first_step = True
            return True
    except Exception as e:
        console.put_string(f"Problem during Intel hex file load: {type(e).__name__}, {str(e)}")
        return False

def input_command(arg_list):
    if len(arg_list) == 1:
        source = FRIDEN_SOURCE_KB if arg_list[0] == 'kb' else FRIDEN_SOURCE_TAPE
        cpu.friden.set_input_source(source)
    console.put_string(f"Input source: kb" if cpu.friden.input_source == FRIDEN_SOURCE_KB else "Input source: tape")


def memreset_command(arg_list):
    cpu.hard_reset()
    return True

def mount_command(arg_list):
    # Args:
    # 0 (optional): Pathname of tape file to mount
    if len(arg_list) == 1:
        if arg_list[0] == '0':
            cpu.friden.close_file()
        else:
            try:
                cpu.friden.open(arg_list[0])
            except:
                console.put_string('Error mounting tape file')
                return False
    if cpu.friden.file is not None:
        console.put_string(f"Mounted: {cpu.friden.pathname}, position = {cpu.friden.file.tell()}")
        return True
    else:
        console.put_string('No tape file mounted')
        return True

def pwd_command(arg_list):
    # Args:
    # None
    cwd = Path.cwd()
    console.put_string(f"Current working directory: {cwd}")
    return True

def reset_command(arg_list):
    cpu.pc.write(cpu.start_address) # reset C/pc to start address
    cpu.first_step = True # restart display
    return True

def run_command(arg_list):
    # Args:
    # None
    if (cpu.friden.file is None) or (cpu.friden.input_source != FRIDEN_SOURCE_TAPE):
        console.put_string('Expecting keyboard input')
    while True:
        result = cpu.step(RUN_MODE_RUN)
        if result == STEP_HALT:
            return result
        else:
            try:
                _ = cpu.friden.get_kb_code()
            except IllegalCharacterError:
                console.put_string('\nRun terminated by non-Friden keyboard input')
                return KB_INTERRUPT
        continue

def start_addr_command(arg_list):
    # Args:
    # 0 (optional): Start address
    if len(arg_list) == 1:
        cpu.start_address = arg_list[0]
        cpu.pc.write(arg_list[0])
        cpu.first_step = True
    console.put_string(f"Start address: {cpu.start_address}") 
    return True

def step_command(arg_list):
    # Args:
    # None
    if (cpu.friden.file is None) or (cpu.friden.input_source != FRIDEN_SOURCE_TAPE):
        console.put_string('Expecting keyboard input')
    return cpu.step(RUN_MODE_STEP)

def list2bitmask(switch_list):
    # For switches command
    # Convert strings to integers
    integer_list = [int(x) for x in switch_list]
    # If the list is empty, return 0
    # otherwise, combine flags using bitwise OR
    bitmask = reduce(or_, integer_list, 0)
    return bitmask
    
def bitmask2string(bitmask):
    # For switches command
    # Define the specific integers to check for
    target_values = [2**5, 2**4, 2**3, 2**2] # [32, 16, 8, 4]
    # Use bitwise AND (&) to find which values are present in the mask
    integer_list = [val for val in target_values if (bitmask & val) != 0]
    switch_str = ' '.join(str(i) for i in integer_list)
    if switch_str.strip() == '':
        switch_str = 'None'
    return switch_str

def switches_command(arg_list):
    # Args:
    # List of switch values
    # A lone value of 0 clears all switches
    # Otherwise 0 is an invalid value
    if (len(arg_list) == 1) and (arg_list[0] == 0):
        cpu.write_switches(0)
    elif (len(arg_list) > 0) and (0 not in arg_list):
        unique_list = sorted(list(set(arg_list)))
        debug_log(f"Unique switches: {unique_list}")
        cpu.write_switches(list2bitmask(unique_list))
    elif (len(arg_list) > 1) and (0 in arg_list):
        console.put_string(f"Invalid switch list: {arg_list}")
        return False
    console.put_string(f"Switches: {bitmask2string(cpu.read_switches())}")     
    return True

def tabs_command(arg_list):
    # Args:
    # List of tab stop values
    # A lone value of zero clears all tab stops
    # Otherwise 0 is an invalid value
    if (len(arg_list) == 1) and (arg_list[0] == 0):
        cpu.friden.write_tab_stops([])
    elif (len(arg_list) > 0) and (0 not in arg_list):
        unique_list = sorted(list(set(arg_list)))
        debug_log(f"Unique tab stops: {unique_list}")
        cpu.friden.write_tab_stops(unique_list)
    elif (len(arg_list) > 1) and (0 in arg_list):
        console.put_string(f"Invalid tab stop(s): {arg_list}")
        return False
    tabs_str = ' '.join(str(i) for i in cpu.friden.read_tab_stops())
    if tabs_str.strip() == '':
        tabs_str = 'None'
    console.put_string(f"Tab stops: {tabs_str}")     
    return True

def tape2drum_command(arg_list):
    # Args:
    # 0: Pathname of tape file to be read into memory
    console.put_string(f"Reading tape file: {arg_list[0]}")
    try:
        tapefile_start_address = tape_loader.tape_to_mem(arg_list[0])
        if tapefile_start_address is not None:
            console.put_string(f"Start address in tape file: {tapefile_start_address}")
            # the start address may subsequently be overridden
            # by a startaddr command
            cpu.start_address = tapefile_start_address
            cpu.pc.write(tapefile_start_address)
            cpu.first_step = True
            return True
    except Exception as e:
        console.put_string(f"Problem during tape load: {type(e).__name__}, {str(e)}")
        return False

def tapemode_command(arg_list):
    # Args:
    # 0 (optional): Tape mode
    if len(arg_list) == 1:
        cpu.friden.mode = text2tapemode[arg_list[0]]
    console.put_string(f"Tape mode: {tapemode2text[cpu.friden.mode]}")
    return True

def tcs_command(arg_list):
    # Args:
    # 0 (optional): transfer control switch (TCS) state
    if len(arg_list) == 1:
        if arg_list[0] == 'on':
            cpu.write_tcs_switch(True)
        else:
            cpu.write_tcs_switch(False)
    if cpu.read_tcs_switch():
        console.put_string('Transfer control switch: On')
    else:
        console.put_string('Transfer control switch: Off')
    return True

def trace_command(arg_list):
    # Args:
    # None
    if (cpu.friden.file is None) or (cpu.friden.input_source != FRIDEN_SOURCE_TAPE):
        console.put_string('Expecting keyboard input')
    for _ in range(int(arg_list[0])):
        result = cpu.step(RUN_MODE_TRACE)
        if result == STEP_HALT:
            return result
        else:
            try:
                _ = cpu.friden.get_kb_code()
            except IllegalCharacterError:
                console.put_string('\nTrace terminated by non-Friden keyboard input')
                return KB_INTERRUPT
        continue

text2tapemode = {
    '4': FRIDEN_MODE_4BIT,
    '6': FRIDEN_MODE_6BIT
    }

tapemode2text = {
    FRIDEN_MODE_4BIT: '4',
    FRIDEN_MODE_6BIT: '6'
    }

commands = {
    # * prefix signifies an optional arg
    'accumulator': (accumulator_init_command, ['*lgp30_integer'], 'set/show accumulator value'),
    'blackjack': (blackjack_command, ['*onoff'], 'set/show blackjack mode (on/off)'),
    'atqdeposit': (atqdeposit_command, ['lgp30_address', 'value', 'qvalue'], 'at address deposit value at q'),
    'atqexamine': (atqexamine_command, ['lgp30_address', 'qvalue'], 'examine memory at address at q'),
    'cd': (cd_command, ['path_d'], 'set the current working directory'),
    'convert': (convert_command, ['lgp30_track_sector'], 'convert TTSS to decimal'),
    'deposit': (deposit_command, ['lgp30_address', 'lgp30_integer'],'at address deposit data'),
    'directory': (dir_command, [], 'list files in the current working directory'),
    'drum2hex': (drum2hex_command, ['path_fw'], 'save Intel hex file'),
    'eatqexamine': (eatqexamine_command, ['lgp30_address', 'eqvalue'], 'examine memory at address at q'),
    'examine': (examine_command, ['lgp30_address', '*lgp30_address'], 'examine memory at address [to address]'),
    'exit': (exit_command, [], 'exit to os'),
    'hex2drum': (hex2drum_command, ['path_fr'], 'load from Intel Hex file'),
    'input': (input_command, ['*source'], 'set/show input source - keyboard (kb) or paper tape file (tape)'),
    'memreset': (memreset_command, [], 'reset memory and registers'),
    'mount': (mount_command, ['*path_fr'], 'mount tape file'),
    'pwd': (pwd_command, [], 'show the current working directory'),
    'reset': (reset_command, [], 'reset C/pc to start address'),
    'run': (run_command, [], 'run'),
    'startaddr': (start_addr_command, ['*lgp30_address'], 'set start address for step or run'),
    'step': (step_command, [],'step'),
    'switches': (switches_command, ['*switch', '*switch', '*switch', '*switch'], \
                 'set switches 32, 16, 8, 4 (0 resets all)'),
    'tabs': (tabs_command, ['*tab', '*tab', '*tab', '*tab', '*tab', '*tab', '*tab', '*tab'], 'set/show up to 8 tab stops (0 resets all)'),
    'tape2drum':(tape2drum_command, ['path_fr'], 'load from paper tape file'),
    'tapemode':(tapemode_command, ['*tapemode'], 'set/show paper tape mode (4 or 6 bits)'),
    'tcs': (tcs_command, ['*onoff'], 'set/show transfer control switch (tcs) state (on or off)'),
    'trace':(trace_command, ['int_value'], 'trace')
    }

validators = {
    'eqvalue': validate_eqvalue,
    'int_value': validate_integer,
    'lgp30_address': validate_lgp30_address,
    'lgp30_integer': validate_lgp30_integer,
    'lgp30_track_sector': validate_lgp30_track_sector,
    'onoff': validate_onoff,
    'path_d': validate_path2dir,
    'path_fr': validate_path4fileread,
    'path_fw': validate_path4filewrite,
    'qvalue': validate_qvalue,
    'source': validate_input_source,
    'switch': validate_switch,
    'tab': validate_tab_stop,
    'tapemode': validate_tapemode,
    'value': validate_value,
    '': validate_no_args
    }

def get_cmd_line_args():    
    cmdline_parser = argparse.ArgumentParser(add_help=False)
    # positional argument (arg1)
    cmdline_parser.add_argument("hex_file_path")
    # optional argument (-a arg2)
    cmdline_parser.add_argument("--ac", type=int)
    # optional argument (-o arg3)
    cmdline_parser.add_argument("--st", type=int)
    # optional argument (-a arg4)
    cmdline_parser.add_argument("-r", action='store_true')
    try:
        args = cmdline_parser.parse_args()
        debug_log(f"Command line args: {args}")
        return args
    except:
        console.put_string('Command line could not be parsed')
        console.put_string('Usage:')
        console.put_string('python sim_lgp30.py hex_file_path ')
        console.put_string('  [--ac=<inital_accumulator_value>]')
        console.put_string('  [--st=<start_address>]')
        console.put_string('  [-r (run)]')
        return None

def process_cmd_line(cmd_line_args):
    command = 'hex2drum ' + cmd_line_args.hex_file_path
    debug_log(f"Dispatching {command} from command line")
    dispatch_command(command)
    if cmd_line_args.ac is not None:
        command = 'accumulator ' + str(cmd_line_args.ac)
        debug_log(f"Dispatching {command} from command line")
        dispatch_command(command)
    if cmd_line_args.st is not None:
        command = 'startaddr ' + str(cmd_line_args.st)
        debug_log(f"Dispatching {command} from command line")
        dispatch_command(command)
    if cmd_line_args.r:
        command = 'run'
        debug_log(f"Dispatching {command} from command line")
        dispatch_command(command)

def get_line():
    console.put_string('--> ', end='')
    line = ''
    while True:
        if console.char_available():
            char = console.get_char()
            if char == '\b':
                if len(line) > 0:
                    console.put_string('\b \b', end='')
                    line = line[:-1]
            elif char in ['\r', '\n']:
                console.put_string('')
                return line.lower()
            elif char.isprintable():
                console.put_string(char, end='')
                line = line + char
        else:
            time.sleep(0.1)

def get_console_command():
    command_list  = []
    while len(command_list) != 1:
        input_text = get_line()
        input_elements = input_text.split()
        if len(input_elements) > 0:
            input_cmd = input_elements[CMDLINE_CMD_INDEX]
            debug_log(f"Got {input_cmd} from console")
            for command in commands:
                if len(input_cmd) <= len(command):
                    if input_cmd == command[0:len(input_cmd)]:
                        debug_log(f"Appending candidate : {command}")
                        command_list.append(command)
            debug_log(f"Candidates: {command_list}")
            if len(command_list) == 1:
                input_elements[CMDLINE_CMD_INDEX] = command_list[0]
                return ' '.join(input_elements)
            else:
                console.put_string('Ambiguous or unrecognised command')
                print_help()
                command_list = []
                return ''
        else:
            print_help()
            return ''

def dispatch_command(command):
# This is a bit wordy but it works, for now
# Firstly validate the argument(s) - the wordy bit
# Then dispatch to the relevant command processor

    def mandatory(validator_id):
        # IDs for mandatory args are not prefixed
        if validator_id is not None:
            if validator_id[0] != '*':
                return True
            else:
                return False
        else:
            return False
            
    def optional(validator_id):
        # IDs for optional args are prefixed with *
        if validator_id is not None:
            if validator_id[0] == '*':
                return True
            else:
                return False
        else:
            return True
    
    elements = command.split()
    debug_log(f"Command elements: {elements}")
    if len(elements) > 0 and elements[CMDLINE_CMD_INDEX] in commands:
        debug_log(f'Got command: {elements[CMDLINE_CMD_INDEX]}')
        command_table_entry = commands[elements[CMDLINE_CMD_INDEX]]
        debug_log('Command table entry: ' + repr (command_table_entry))
        command_processor = command_table_entry[CMDTBL_CMD_PROCESSOR_INDEX]
        debug_log('Command processor ' + repr(command_processor))
        validator_list = command_table_entry[CMDTBL_ARG_LIST_INDEX]
        debug_log('Validator list: ' + repr(validator_list))
        # Validate the args (elements 1..)
        # A validator must return a validated value, or None
        pairs = list(itertools.zip_longest(validator_list, elements[CMDLINE_FIRST_ARG_INDEX:]))
        # (unmatched members on either side are paired with None)
        debug_log(f"Validator, element pairs: {pairs}")
        all_valid = True # init for final result
        one_valid = True # init for first arg
        validated_args = [] # ready to receive validated args
        for (validator, element) in pairs:
            if validator and mandatory(validator) and element:
                val_result = validators[validator](element)
                one_valid = one_valid and (val_result is not None)
                if one_valid:
                    validated_args.append(val_result)
            elif validator and mandatory(validator) and not element:
                one_valid = False
            elif validator and optional(validator) and element:
                val_result = validators[validator[1:]](element) # exclude the *
                one_valid = one_valid and (val_result is not None)
                if one_valid:
                    validated_args.append(val_result)
            elif validator and optional(validator) and not element:
                pass
            elif not validator and element:
                one_valid = False
            debug_log(f"V: {validator}, E: {element}, one_valid: {one_valid}")
            all_valid = all_valid and one_valid # update final result
            if not all_valid:
                break # no need to continue
            one_valid = True # re-init for next arg
        debug_log(f"all_valid: {all_valid}")
        if all_valid:
            debug_log(f"Validated args: {validated_args}")
            # And away we go
            result = command_processor(validated_args)
            debug_log(f"Result = {result}")
        else:
            console.put_string(f"Invalid argument(s): {elements[CMDLINE_FIRST_ARG_INDEX:]}")
    else:
        # The command has already been validated, so nothing to do here
        pass

cpu = LGP30_CPU(debug_log) # initialised from BLANK drum
hexfile_loader = HexfileLoader(cpu.drum.mem, debug_log)
tape_loader = TapeLoader(cpu.drum.mem, debug_log)

def main():
    print_splash()
    cmd_line_args = get_cmd_line_args()
    if cmd_line_args:
        process_cmd_line(cmd_line_args)
    else:
        sys.exit(1)
    while True:
        command = get_console_command()
        dispatch_command(command)

if __name__ == "__main__":
    main()
