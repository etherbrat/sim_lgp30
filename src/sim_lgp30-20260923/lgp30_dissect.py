from sim_lgp30.simulator_constants import * 

MNEMONICS = {
    0: 'z',
    1: 'b',
    2: 'y',
    3: 'r',
    4: 'i',
    5: 'd',
    6: 'n',
    7: 'm',
    8: 'p',
    9: 'e',
    10: 'u',
    11: 't',
    12: 'h',
    13: 'c',
    14: 'a',
    15: 's'
    }

def value2sex(value):
    # No need for lobal constants
    WORD_MASK = 0xffffffff
    SEX_DIGITS_PER_GROUP = 8
    BITS_PER_DIGIT = 4
    DIGIT_MASK = 15
    SEX_CHARSET = {
        0: '0', 
        1: '1',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
        7: '7',
        8: '8', 
        9: '9',
        10: 'f',
        11: 'g',
        12: 'j', 
        13: 'k', 
        14: 'q',
        15: 'w'
        }   
    _value = value & WORD_MASK # limit to 8 digits
    sex = ''
    for i in range(SEX_DIGITS_PER_GROUP):
        digit_value = _value & DIGIT_MASK
        _value = _value >> BITS_PER_DIGIT
        digit_char = SEX_CHARSET[digit_value]
        sex = digit_char + sex
    return sex

def addr2track(addr):
    return (addr & LGP30_ADDR_TRACK_MASK) >> LGP30_ADDR_TRACK_SHIFT

def addr2sector(addr):
    return (addr & LGP30_ADDR_SECTOR_MASK)

def instr2opcode(instr_word):
    return (instr_word & LGP30_OPCODE_MASK) >> LGP30_OPCODE_SHIFT

def instr2operand_addr(instr_word):
    return (instr_word & LGP30_ADDRESS_MASK) >> LGP30_ADDRESS_SHIFT

def instr2operand_track(instr_word):
    return (instr_word & LGP30_TRACK_MASK) >> LGP30_TRACK_SHIFT

def instr2operand_sector(instr_word):
    return (instr_word & LGP30_SECTOR_MASK) >> LGP30_SECTOR_SHIFT

def instr2mnemonic(instr_word):
    mnemonic =  MNEMONICS[instr2opcode(instr_word)]
    if mnemonic == 't' and (instr_word & LGP30_SIGN_MASK != 0):
        return '*t'
    else:
        return mnemonic

def disassemble_instr(instr_word):
    # Will usually be called after the fetch, such that:
    # self.pc.prev() is the relevant pc value and
    # self.ir.val() is the relevant ir value.
    # On the very first step (no previous pc),
    # self.pc.prev() and self.pc.val() will both be initialised
    # to the initial pc value, so all good
    if instr_word is not None:
        disassembly = {}
        disassembly['dec'] = f"{instr_word:10}"
        disassembly['sex'] = f"{value2sex(instr_word)}" # always 8 sex digits
        disassembly['hex'] = f"{instr_word:08x}"
        disassembly['opcode'] = f"{instr2opcode(instr_word):2}"
        disassembly['mnem'] = f"{instr2mnemonic(instr_word):>2}" # all are length 1 except sometimes *t
        disassembly['operand_addr'] = f"{instr2operand_addr(instr_word):4}"
        disassembly['operand_track'] = f"{instr2operand_track(instr_word):2}"
        disassembly['operand_sector'] = f"{instr2operand_sector(instr_word):2}"
        return disassembly
    else:
        return None

def render_disassembly(d): # d for disassembly
    if d is not None:
        return f"{d['dec']} {d['sex']} {d['hex']} {d['opcode']} {d['mnem']} {d['operand_addr']} {d['operand_track']} {d['operand_sector']}"
    else:
        return f"{'None':>10}"

def show_address(address, data):
    addr_string = f"{address:4} {addr2track(address):2} {addr2sector(address):2}" if address is not None else 'None'
    d = disassemble_instr(data)
    data_string = f"{render_disassembly(d)}"
    print(f"{addr_string}: {data_string}")
