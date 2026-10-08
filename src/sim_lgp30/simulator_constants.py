DEBUG = False
LGP30_STRICT = False # True if we want halting for None values

BITS32 = False # for testing purposes only (appends spare bit to disassembly)

SIM_LGP30_VERSION = 1.0

# masks and shifts for C/pc
LGP30_ADDR_TRACK_MASK = 0xfc0
LGP30_ADDR_TRACK_SHIFT = 6
LGP30_ADDR_SECTOR_MASK = 0x3f

# masks and shifts for a 32-bit word
LGP30_SIGN_MASK = 0x80000000
LGP30_BIT33_MASK = 0x100000000
LGP30_WORD_MASK = 0xffffffff
LGP30_ZERO_SPACER = 0xfffffffe
LGP30_OPCODE_MASK = 0x000f0000
LGP30_OPCODE_SHIFT = 16
LGP30_ADDRESS_MASK = 0x00003ffc
LGP30_ADDRESS_SHIFT = 2
LGP30_TRACK_MASK = 0x00003f00
LGP30_TRACK_SHIFT = 8
LGP30_SECTOR_MASK = 0x000000fc
LGP30_SECTOR_SHIFT = 2

LGP30_M_MASK = 0x7fffffff00000000
LGP30_M_SHIFT = 31
LGP30_N_MASK = 0x00000000fffffffe
LGP30_N_SHIFT = 0
LGP30_D_SCALE = 2**31
LGP30_D_MASK = 0xfffffffe

LGP30_MIN_INT = -(2**30)  
LGP30_MAX_INT = (2**30)-1
LGP30_MIN_ADDR = 0
LGP30_MAX_ADDR = 4095
LGP30_NUM_TRACK_SECTOR_DIGITS = 4
LGP30_NUM_TRACKS = 64
LGP30_SECTORS_PER_TRACK = 64

LGP30_MIN_QVALUE = 0
LGP30_MAX_QVALUE = 30
LGP30_MIN_EQVALUE = 0
LGP30_MAX_EQVALUE = 61
LGP30_EATQ_SHIFT = 31
LGP30_EWORD_MASK = 0x3fffffffffffffff
LGP30_ESIGN_MASK = 0x2000000000000000

DEFAULT_START_ADDRESS = 0

# run modes
RUN_MODE_STEP = 0
RUN_MODE_RUN = 1
RUN_MODE_TRACE = 2

# step results
STEP_CONTINUE = 0
STEP_HALT = 1
KB_INTERRUPT = 2

# tab stop support
MAX_TAB_STOP = 100

CMDLINE_CMD_INDEX = 0
CMDLINE_FIRST_ARG_INDEX = 1

CMDTBL_CMD_PROCESSOR_INDEX = 0
CMDTBL_ARG_LIST_INDEX = 1
CMDTBL_HELP_TEXT_INDEX = 2

OPCODE_LOOKUP = {
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

class IllegalCharacterError(IOError):
    pass

class IllegalCodeError(IOError):
    pass

class InputTimeoutError(IOError):
    pass
