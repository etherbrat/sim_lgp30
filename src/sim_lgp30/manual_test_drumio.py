import sys

import random

LGP30_SIGN_MASK = 0x80000000
LGP30_WORD_MASK = 0xffffffff


def drum2python(drum_val):
    # C/pc has 12 (active) bits. R/ir has 4 (active) bits.
    # A/ac has 32 bits. 
    # A drum memory location has 32-bits, including a zero
    # bit in the LSB (the spacer bit).
    # Python has an infinite precision integer.
    # Bitwise operations in Python behave as if the argument
    # is an infintely sign extended twos compliment value.
    # This routine converts 32 bits. Others are responsible
    # for maintaining valid content.
    if drum_val is not None:
        sign = drum_val & LGP30_SIGN_MASK
        if sign != 0:
            # negative
            return 0 - ((drum_val ^ LGP30_WORD_MASK) + 1)
        else:
            return drum_val
    else:
        return None

def python2drum(py_val):
    # C/pc has 12 (active) bits. R/ir has 4 (active) bits.
    # A/ac has 32 bits. A drum memory location has 32-bits,
    # including a zero bit in the LSB (the spacer bit).
    # Python has an infinite precision integer.
    # Bitwise operations in Python behave as if the argument
    # is an infintely sign extended twos compliment value.
    # This routine converts 32 bits. Others are responsible
    # for maintaining valid content.
    #
    # This function will be used for writing C/pc and R/ir,
    # both of which can validly contain an odd number;
    # therefore it must not mask the LSB to zero.
    if py_val is not None:
        return py_val & LGP30_WORD_MASK            
    else:
        return None

# Fuzz the interior
# Round trip from Python
print('Fuzz')
for _ in range (10000):
    pin_val = random.randint(-2**31, 2**31-1)
    print(pin_val)
    nin_val = -pin_val
    pin_val = python2drum(pin_val)
    nin_val = python2drum(nin_val)
    if drum2python(pin_val) + drum2python(nin_val) != 0:
        print('Eeek!')
        sys.exit()
#
# Enumerate the extrema
# Round trip from Python
print('Enumerate')
for pin_val in [-(2**31-1), -(2**31-2), -(2**31-3), -2, -1, 0, 1, 2, 2**31-3, 2**31-2, 2**31-1]:
    print(pin_val)
    nin_val = -pin_val
    pin_val = python2drum(pin_val)
    nin_val = python2drum(nin_val)
    if drum2python(pin_val) + drum2python(nin_val) != 0:
        print('Eeek!')
        sys.exit()
    