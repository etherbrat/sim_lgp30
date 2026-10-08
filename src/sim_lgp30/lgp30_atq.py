from sim_lgp30.simulator_constants import *

import math # for math.modf()

def atq2python(frac, q):
    # sign exend if necessary
    if frac & LGP30_SIGN_MASK:
        return (0 - ((frac ^ LGP30_WORD_MASK) + 1)) * 2**(q-31)
    else:
        return frac * 2**(q-31)
        
# Note: This function takes an un-offset 62-bit two's complement binary value
def eatq2python(frac, q):
    # sign exend if necessary
    if frac & LGP30_ESIGN_MASK:
        return (0 - ((frac ^ LGP30_EWORD_MASK) + 1)) * 2**(q-61)
    else:
        return frac * 2**(q-61)
        
def python2atq(value, q):
    (f, i) = math.modf(value / (2**q))
    if i != 0:
        raise ValueError(f"{value} is non-fractional at q = {q}")
    else: 
        return int(f * 2**31) & LGP30_ZERO_SPACER

# Note: This function produces an un-offset 62-bit two's complement binary value
def python2eatq(value, q):
    (f, i) = math.modf(value / (2**q))
    if i != 0:
        raise ValueError(f"{value} is non-fractional at q = {q}")
    else:
        return int(f * 2**61) & LGP30_EWORD_MASK
