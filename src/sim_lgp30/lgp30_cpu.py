# Objectives:
# Make sure that register and memory writes invariably go to the drum.
# Make sure that local copies are invariably in sync with the values
# on the drum.
# Keep the single previous value of each register, and of the single
# most recently accessed location.
# Make sure that C/pc increment invariably follows instruction fetch.
# Perform accurate, if not perfectly authentic, arithmetic.

# Achieve by:
# Ensure that the drum is the reference for all values, register
# and memory.
# There are two classes of read access: The first (read) by an
# LGP-30 instruction to retrieve the contents of a memory location,
# and the second (val) by the simulator, mid-instruction, for
# calculation or display.
# LGP-30 instruction performs a read: Read the drum to a local
# copy. The previous value is the same as the current value.
# LGP-30 instruction performs a write: Read the drum to establish
# the previous value, keep the new value as the current value and
# write it to the drum.
# After 'showing' any change, the previous value is set to the
# current value.
# For the LGP-30, there is no change of memory address in
# mid-instruction, hence no need to track multiple addresses.

# step(self, mode) is the only entry point. The mode must be specified
# for each step. step() returns a STEP_<result> which indicates to the
# caller what should happen next. Continuous running is achieved by
# repeatedly calling step() with mode = 'run'.

import sys # for sys.exit

import math # for math.modf()

from sim_lgp30.simulator_constants import *

from sim_lgp30.friden_constants import FRIDEN_MODE_4BIT, FRIDEN_MODE_6BIT, CHAR_STOP

import sim_lgp30.console_nonblock as console

from sim_lgp30.lgp30_dissect import *

from sim_lgp30.lgp30_drum import LGP30_Drum

from sim_lgp30.lgp30_friden import Friden

# tuple indices in output codeset dict
CHAR_DESC = 0
CHAR_UPPER = 1
CHAR_LOWER = 2

OUTPUT_CODESET = {
    # key is track number
    0:('start','',''),
    1:('Z z','Z','z'),
    2:(') 0',')','0'),
    3:('space',' ',' '),
    4:('lower','',''),
    5:('B b','B','b'),
    6:('L l 1','L','l'),
    7:('_ -','_','-'),
    8:('upper','',''),
    9:('Y y','Y','y'),
    10:('* 2','*','2'),
    11:('= +','=','+'),
    12:('colour','',''),
    13:('R r','R','r'),
    14:('" 3','"','3'),
    15:(': ;',':',';'),
    16:('return','',''),
    17:('I i','I','i'),
    18:('Δ 4','Δ','4'),
    19:('? /','?','/'),
    20:('backsp','',''),
    21:('D d','D','d'),
    22:('% 5','%','5'),
    23:('] .',']','.'),
    24:('tab','',''),
    25:('N n','N','n'),
    26:('$ 6','$','6'),
    27:('[ '+',','[',','),
    28:('unused','',''),
    29:('M m','M','m'),
    30:('∏ 7','∏','7'),
    31:('V v','V','v'),
    32:('stop','',''),
    33:('P p','P','p'),
    34:('Σ 8','Σ','8'),
    35:('O o','O','o'),
    36:('unused','',''),
    37:('E e','E','e'),
    38:('( 9','(','9'),
    39:('X x','X','x'),
    40:('unused','',''),
    41:('U u','U','u'),
    42:('F f','F','f'),
    43:('unused','',''),
    44:('unused','',''),
    45:('T t','T','t'),
    46:('G g','G','g'),
    47:('unused','',''),
    48:('unused','',''),
    49:('H h','H','h'),
    50:('J j','J','j'),
    51:('unused','',''),
    52:('unused','',''),
    53:('C c','C','c'),
    54:('K k','K','k'),
    55:('unused','',''),
    56:('unused','',''),
    57:('A a','A','a'),
    58:('Q q','Q','q'),
    59:('unused','',''),
    60:('unused','',''),
    61:('S s','S','s'),
    62:('W w','W','w'),
    63:('delete','','')
    }

def sign_extend(val32):
    if val32 is not None:
        sign = val32 & LGP30_SIGN_MASK
        if sign != 0:
            # negative
            return 0 - ((val32 ^ LGP30_WORD_MASK) + 1)
        else:
            return val32
    else:
        return None
    
class Register():
# Assumed: The value type is immutable
# Keep one previous value

    def __init__(self, name, read_proc, write_proc):
        self.name = name
        self.read_proc = read_proc
        self.write_proc = write_proc
        self.value = None
        self.prev_value = None

    def hard_reset(self):
        self.value = None
        self.prev_value = None
        
    def nom(self):
        return self.name
        
    def write(self, value):
        self.prev_value = self.read_proc()
        self.value = value
        self.write_proc(value)

    def read(self):    
        self.value = self.read_proc()
        self.prev_value = self.value
        return self.value
    
    def val(self):
        return self.value
        
    def prev(self):
        return self.prev_value
    
class Memory():
# Assumed: The value type is immutable
# Keep one previous value for the most recently read or written address
# There are belts-and braces checks on the LSB of the value written or read

    def __init__(self, name, read_proc, write_proc):
        self.name = name
        self.read_proc = read_proc
        self.write_proc = write_proc
        self.address = None
        self.value = None
        self.prev_value = None

    def hard_reset(self):
        self.address = None
        self.value = None
        self.prev_value = None
       
    def addr(self):
        return self.address
        
    def nom(self):
        return self.name
        
    def write(self, address, value):
        self.address = address
        if address is not None:
            self.prev_value = self.read_proc(address)
            self.value = value
            if (value is None): 
                if LGP30_STRICT:
                    console.put_string(f"Warning: None value written to memory, {address}: {value}")
            else:
                if value & 1 != 0:
                    console.put_string(f"Warning: Non-zero LSB in value written to memory, {address}: {value}")
            self.write_proc(address, value)
        else:
            self.prev_value = None
            self.value = None
        
    def read(self, address):
        if address is not None:
            self.value = self.read_proc(address)
            self.prev_value = self.value
            if (self.value is None):
                if LGP30_STRICT:
                    console.put_string(f"Warning: None value read from memory, {address}: {self.value}")
            else:
                if self.value & 1 != 0:
                    console.put_string(f"Warning: Non-zero LSB in value read from memory, {address}: {self.value}")
            return self.value
        else:
            return None
    
    def val(self):
        return self.value
   
    def prev(self):
        return self.prev_value
    
class LGP30_CPU():
    # The _<mnemonic>_op operations are executed occur after a fetch. As such, it is assumed that:
    # C/pc has been post-incremented, i.e. self.pc.prev() is the address of the current instruction, and
    # self.ir.val() specifies the operation to be executed.
    # No assumptions are made about the state of self.ac or self.mem.

    def instr2tcs_bit(self, instr_word):
        return True if instr_word & LGP30_SIGN_MASK != 0 else False
    
    def _z_op(self):
            # Stop:
            # z 0000 (or 3200, or 1600, or 0800, or 0400) 
            # If computation is to stop, the address portion of the stop instruction
            # is usually of no significance.
            # However, the stop instruction has a special characteristic:
            # Four break point switches (called Break Point 32, Break Point 16, Break Point 8 and Break Point 4)
            # are supported by the z instruction. There is a 1:1 correspondence between these switches
            # and the four most significant bits of the track number.
            # Computation does not stop if a break point switch is latched down
            # and the corresponding bit is set in the track number.
            # self.debug_log("CPU: _z_op")
            if self.blackjack_mode:
                return STEP_CONTINUE
            else:
                switch_spec = (self.ir.val() & LGP30_TRACK_MASK) >> LGP30_TRACK_SHIFT
                if switch_spec & self.switches != 0:
                    return STEP_CONTINUE
                else:
                    return STEP_HALT
    
    def _b_op(self):
        # Bring:
        # b 2000
        # Replace the word in the A register with the word in memory location 2000.
        # The contents of memory location 2000 are unaffected.
        self.debug_log("CPU: _b_op")
        operand_address = instr2operand_addr(self.ir.val())
        operand = self.mem.read(operand_address)
        if operand is None:
            console.put_string(f"None operand at {operand_address} in b instruction at {self.pc.prev()}")
            return STEP_HALT
        else:
            self.ac.write(operand)
            return STEP_CONTINUE
    
    def _y_op(self):
        # Store address:
        # y 2000
        # Replace the address portion of the word in memory location 2000 with
        # the address portion of the word in the A register.
        # The contents of the A register are unaffected.
        # The LGP-30 has no index register. This instruction can be used to self-modify code to index an array.
        self.debug_log("CPU: _y_op")
        operand_address = instr2operand_addr(self.ir.val())
        target_instr = self.mem.read(operand_address)
        if target_instr is None:
            console.put_string(f"None operand at {operand_address} in y instruction at {self.pc.prev()}")
            return STEP_HALT
        ac_val = self.ac.read()
        if ac_val is None:
            console.put_string(f"None A/ac in y instruction at {self.pc.prev()}")
            return STEP_HALT
        new_addr = ac_val & LGP30_ADDRESS_MASK
        modified_instr = (target_instr & ~LGP30_ADDRESS_MASK) | new_addr
        self.mem.write(operand_address, modified_instr)
        return STEP_CONTINUE
    
    def _r_op(self):
        # Return address:
        # r 2000
        # Add one to the value of the C register (do not update the C register), then replace the
        # address portion of the word in location 2000 with this value. R is followed immediately
        # by an unconditional transfer instruction to the beginning of the subroutine.
        # This instruction is used to patch an unconditional transfer instruction at the end of a
        # subroutine, redirecting execution to the instruction following the invoking transfer.
        # R can also be used to patch a Test instruction in order to create a conditional return.
        self.debug_log("CPU: _r_op")
        return_address = self.pc.val() + 1 ; # u instr is next, then the return target
        operand_address = instr2operand_addr(self.ir.val())
        target_instr = self.mem.read(operand_address)
        if target_instr is None:
            console.put_string(f"None operand at {operand_address} in r instruction at {self.pc.prev()}")
            return STEP_HALT
        new_addr = return_address << LGP30_ADDRESS_SHIFT
        modified_instr = (target_instr & ~LGP30_ADDRESS_MASK) | new_addr
        self.mem.write(operand_address, modified_instr)
        return STEP_CONTINUE
    
    def _i_op(self):
        # Input:
        # i 0000
        # The address portion of this instruction is always 0000. It is always preceded
        # by the instruction p 0000.
        # After a p 0000 instruction starts the tape reader, an i 0000 instruction transfers
        # into the last 4 bit positions of the A register the first 4 bits of the typewriter code
        # for the first character read on the tape. When the second character is read,
        # the bits representing the first character are shifted left into the next to last
        # four bit positions of the A register and the first four bits of the typewriter code
        # of the second character on tape are placed in the last four bit positions of the A register.
        # This process continues up to eight times to fill the entire A register
        # until a stop code (100000) appears on the tape. The stop code stops the tape reader
        # and sends a start signal to the computer so that the instruction following i 0000 in memory
        # is executed. Often this next instruction is a h or c instruction so that
        # the characters read into the A register can be stored in a memory location.
        #
        # The paper tape reader (ptr) returns characters through the same channel
        # as the keyboard (kb). The LGP-30 has a switch for selecting input from either
        # the kb or the ptr. The program should treat kb input and ptr (file) input
        # identically. In both cases cases:
        # Use non-blocking character input with a timeout.
        # On Friden character received: Process into A/ac as per 4-bit or 6-bit
        # mode.
        # On stop character received: Complete the instruction.
        # On non-Friden character received: Process the invalid character exception.
        # On EoF: Process the EoF exception.
        # On timeout: Process the timeout exception.
        # In any of the exceptional cases, the state of A/ac will be indeterminate.
        # See lgp30_friden for low-level processing.
        self.debug_log("CPU: _i_op")
        while True:
            try:
                in_code = self.friden.await_code()
            except IllegalCharacterError:
                console.put_string('\nInput terminated by non-Friden character')
                return STEP_HALT
            except InputTimeoutError:
                console.put_string('\nInput terminated by timeout')
                return STEP_HALT
            except IOError:
                console.put_string('\nInput terminated - no tape file')
                return STEP_HALT
            except EOFError:
                console.put_string('\nInput terminated - end of tape file')
                return STEP_HALT
            # except Exception as e:
            #     console.put_string(f"\nInput terminated abnormally with {type(e).__name__}: {str(e)}")
            #     return STEP_HALT
            else:
                if self.run_mode == RUN_MODE_STEP:
                    console.put_string(f"From keyboard: {in_code}")
                if in_code == CHAR_STOP:
                    return STEP_CONTINUE
                ac_val = self.ac.read()
                if (ac_val is None):
                    if LGP30_STRICT:
                        console.put_string(f"None A/ac in i instruction at {self.pc.prev()}")
                        return STEP_HALT
                    else:
                        console.put_string(f"None A/ac in i instruction at {self.pc.prev()}, substituting zero")
                        ac_val = 0
                if self.friden.mode == FRIDEN_MODE_4BIT:
                    self.ac.write((ac_val << 4) | in_code)
                else: # self.friden.mode = FRIDEN_MODE_6BIT
                    self.ac.write((ac_val << 6) | in_code)
           
    def _d_op(self):
        # Divide:
        # d 2000
        # Divide the number in the A register by the number in memory location 2000 and
        # place the quotient, rounded to thirty bits, in the A register.
        # The contents of memory location 2000 are unaffected.
        self.debug_log("CPU: _d_op")
        operand_address = instr2operand_addr(self.ir.val())
        divisor = sign_extend(self.mem.read(operand_address))
        if divisor is None:
            console.put_string(f"None operand at {operand_address} in d instruction at {self.pc.prev()}")
            return STEP_HALT
        dividend = sign_extend(self.ac.read())
        if dividend is None:
            console.put_string(f"None A/ac in d instruction at {self.pc.prev()}")
            return STEP_HALT
        fractional_part, integer_part = math.modf(dividend / divisor)
        # Overflow if the integer part is non-zero
        if integer_part != 0:
            console.put_string(f"Division overflow in d instruction at {self.pc.prev()}")
            return STEP_HALT
        else:
            quotient = (round(fractional_part * LGP30_D_SCALE)) & LGP30_D_MASK
            self.ac.write(quotient)
            return STEP_CONTINUE
    
    def _n_op(self):
        # Multiply lower:
        # n 2000
        # Multiply the number in the A register by the number in memory location 2000 and
        # place the least significant thirty-one magnitude bits of the product in
        # the sign bit and thirty magnitude bits of the A register.
        # The contents of memory location 2000 are unaffected.
        self.debug_log("CPU: _n_op")
        operand_address = instr2operand_addr(self.ir.val())
        multiplier = sign_extend(self.mem.read(operand_address))
        if multiplier is None:
            console.put_string(f"None operand at {operand_address} in n instruction at {self.pc.prev()}")
            return STEP_HALT
        multiplicand = sign_extend(self.ac.read())
        if multiplicand is None:
            console.put_string(f"None A/ac in n instruction at {self.pc.prev()}")
            return STEP_HALT
        n_product = ((multiplicand * multiplier) & LGP30_N_MASK) >> LGP30_N_SHIFT
        self.ac.write(n_product)
        return STEP_CONTINUE
    
    def _m_op(self):
        # Multiply upper:
        # m 2000
        # Multiply the number in the A register by the number in memory location 2000 and
        # place the most significant thirty bits of the product in the A register.
        # The contents of memory location 2000 are unaffected.
        self.debug_log("CPU: _m_op")
        operand_address = instr2operand_addr(self.ir.val())
        multiplier = sign_extend(self.mem.read(operand_address))
        if multiplier is None:
            console.put_string(f"None operand at {operand_address} in m instruction at {self.pc.prev()}")
            return STEP_HALT
        multiplicand = sign_extend(self.ac.read())
        if multiplicand is None:
            console.put_string(f"None A/ac in m instruction at {self.pc.prev()}")
            return STEP_HALT
        m_product = ((multiplicand * multiplier) & LGP30_M_MASK) >> LGP30_M_SHIFT
        self.ac.write(m_product)
        return STEP_CONTINUE      

    def _p_op(self):
        # Print:
        # p 2000
        # Execute the typewriter keyboard function indicated by the 6 track bits.
        # The print order has no effect on the contents of any memory location, the A register,
        # or the C register. For example, p 2000 has 010100 in the track bits
        # which is the code for a back space on the typewriter.
        # The execution of p 2000 results in the typewriter back spacing.
        self.debug_log("CPU: _p_op")
        friden_code = (self.ir.val() & LGP30_TRACK_MASK) >> LGP30_TRACK_SHIFT
        self.friden.put_code(friden_code)
        return STEP_CONTINUE
    
    def _e_op(self):
        # Extract: (Logical AND)
        # e 2000
        # Place zeroes in the word in the A register wherever there are zeroes in location 2000
        # but otherwise leave the word in the A register unchanged.
        # The contents of memory location 2000 are unaffected.
        self.debug_log("CPU: _e_op")
        operand_address = instr2operand_addr(self.ir.val())
        val1 = self.mem.read(operand_address)
        if val1 is None:
            console.put_string(f"None operand at {operand_address} in e instruction at {self.pc.prev()}")
            return STEP_HALT
        val2 = self.ac.read()
        if val2 is None:
            console.put_string(f"None A/ac in e instruction at {self.pc.prev()}")
            return STEP_HALT
        valand = val1 & val2
        self.ac.write(valand)
        return STEP_CONTINUE
    
    def _u_op(self):
        # Unconditional transfer:
        # u 2000
        # Replace the word in the C register with the address portion of this instruction.
        self.debug_log("CPU: _u_op")
        self.pc.write(instr2operand_addr(self.ir.val()))
        return STEP_CONTINUE
    
    def _t_op(self):
        # Test (Conditional transfer):
        # t 2000
        # If the sign bit of the A register is a 1, the test instruction has the effect of
        # an unconditional transfer.
        # If the sign bit of the A register is a 0, the next instruction in the normal sequence
        # is executed.
        # But note: When the transfer control switch (TCS) is on:
        # If a test instruction has the sign bit (normally unused in an instruction word) set,
        # a transfer will take place unconditionally, i.e. regardless of the accumulator's value.
        self.debug_log("CPU: _t_op")
        ac_val = self.ac.read()
        if ac_val is None:
            console.put_string(f"None A/ac in t instruction at {self.pc.prev()}")
            return STEP_HALT
        if (ac_val & LGP30_SIGN_MASK) or ((self.ir.val() & LGP30_SIGN_MASK) and self.tcs_switch):
            self.pc.write(instr2operand_addr(self.ir.val()))
        return STEP_CONTINUE
  
    def _h_op(self):
        # Store and hold:
        # h 2000
        # Replace the word in memory location 2000 with word in the A register.
        # The contents of the A register are unaffected.
        self.debug_log("CPU: _h_op")
        ac_val = self.ac.read()
        if ac_val is None:
            console.put_string(f"None A/ac in h instruction at {self.pc.prev()}")
            return STEP_HALT
        self.mem.write(instr2operand_addr(self.ir.val()), ac_val & LGP30_ZERO_SPACER)
        return STEP_CONTINUE
    
    def _c_op(self):
        # Store and clear:
        # c 2000
        # Replace the word in memory location 2000 with the word in the A register,
        # then zero the A register.        
        self.debug_log("CPU: _c_op")
        ac_val = self.ac.read()
        if ac_val is None:
            if LGP30_STRICT:
                console.put_string(f"None A/ac in c instruction at {self.pc.prev()}")
                return STEP_HALT
            else:
                console.put_string(f"None A/ac in c instruction at {self.pc.prev()} - substituting zero")
                ac_val = 0
        self.mem.write(instr2operand_addr(self.ir.val()), ac_val & LGP30_ZERO_SPACER)
        self.ac.write(0)
        return STEP_CONTINUE

    # In general, any two N-bit numbers may be added without overflow, by first sign-extending
    # both of them to N + 1 bits, and then adding. The N + 1 bits result is large enough
    # to represent any possible sum, so overflow will never occur. It is then possible, if desired,
    # to 'truncate' the result back to N bits while preserving the value if, and only if,
    # the discarded bit is a proper sign extension of the retained result bits. This provides
    # a method of detecting overflow, which may be preferable in situations that do not have
    # access to the internals of the addition.

    def _a_op(self):
        # Add:
        # a 2000
        # Add the word in memory location 2000 to the A register and place the result in the A register.
        # The contents of memory location 2000 are unaffected.
        self.debug_log("CPU: _a_op")
        operand_address = instr2operand_addr(self.ir.val())
        addend = sign_extend(self.mem.read(operand_address))
        if addend is None:
            console.put_string(f"None operand at {operand_address} in a instruction at {self.pc.prev()}")
            return STEP_HALT
        augend = sign_extend(self.ac.read())
        if augend is None:
            console.put_string(f"None A/ac in a instruction at {self.pc.prev()}")
            return STEP_HALT
        addsum = addend + augend
        # Overflow test
        if bool(addsum & LGP30_SIGN_MASK) ^ bool(addsum & LGP30_BIT33_MASK):
            console.put_string(f"Addition overflow at {self.pc.prev()}")
            return STEP_HALT
        else:
            self.ac.write(addsum & LGP30_WORD_MASK) # keep the LSB (if any) for now
            return STEP_CONTINUE
    
    def _s_op(self):
        # Subtract:
        # s 2000
        # Subtract the word in memory location 2000 from the A register and place the result in the A register,
        # The contents of memory location 2000 are unaffected.
        self.debug_log("CPU: _s_op")
        operand_address = instr2operand_addr(self.ir.val())
        subtrahend = sign_extend(self.mem.read(operand_address))
        if subtrahend is None:
            console.put_string(f"None operand at {operand_address} in s instruction at {self.pc.prev()}")
            return STEP_HALT
        minuend = sign_extend(self.ac.read())
        if minuend is None:
            console.put_string(f"None A/ac in s instruction at {self.pc.prev()}")
            return STEP_HALT
        subdiff = minuend - subtrahend
        # Overflow test
        if bool(subdiff & LGP30_SIGN_MASK) ^ bool(subdiff & LGP30_BIT33_MASK):
            console.put_string(f"Subtraction overflow at {self.pc.prev()}")
            return STEP_HALT
        else:
            self.ac.write(subdiff & LGP30_WORD_MASK) # keep the LSB (if any) for now
            return STEP_CONTINUE
    
    def __init__(self, debug_print_function):
        self.drum = LGP30_Drum()
        # I use Friden and the friden needs to know about me, hence ...
        self.friden = Friden(self)
        self.debug_log = debug_print_function
        self.debug_log("CPU: Initialising LGP-30 CPU")
        self.start_address = DEFAULT_START_ADDRESS
        self.switches = 0
        self.tcs_switch = False
        self.blackjack_mode = False
        self.run_mode = RUN_MODE_STEP
        # working copies of drum entities
        self.pc = Register('C/pc', self.drum.read_pc, self.drum.write_pc)
        self.ir = Register('R/ir', self.drum.read_ir, self.drum.write_ir)
        self.ac = Register('A/ac', self.drum.read_ac, self.drum.write_ac)
        self.mem = Memory('mem', self.drum.read_mem, self.drum.write_mem)
        # housekeeping and reference
        self.first_step = True
        self.operations = {
            0: self._z_op,
            1: self._b_op,
            2: self._y_op,
            3: self._r_op,
            4: self._i_op,
            5: self._d_op,
            6: self._n_op,
            7: self._m_op,
            8: self._p_op,
            9: self._e_op,
            10: self._u_op,
            11: self._t_op,
            12: self._h_op,
            13: self._c_op,
            14: self._a_op,
            15: self._s_op
            }

    def hard_reset(self):
        self.start_address = DEFAULT_START_ADDRESS
        self.switches = 0
        self.tcs_switch = False
        self.blackjack_mode = False
        self.run_mode = RUN_MODE_STEP
        self.pc.hard_reset()
        self.ir.hard_reset()
        self.ac.hard_reset()
        self.mem.hard_reset()
        self.drum.hard_reset()
        self.first_step = True

    def write_switches(self, switches):
        self.switches = switches
    
    def read_switches(self):
        return self.switches

    def write_tcs_switch(self, switch_val):
        self.tcs_switch = switch_val

    def read_tcs_switch(self):
        return self.tcs_switch
        
    def render_pc(self):
        # Renders the C/pc relevant to the current instruction
        # which, after a fetch, is self.pc.prev().
        # After anything that forcilbly sets the pc value
        # such that self.first_step is True,
        # both self.pc.prev() and self.pc.val() are initialised
        # to the starting value of the C/pc, so all good
        if self.pc.prev() is None:
            # This is before the first fetch
            pass
        else:
            # This is before every subsequent fetch
            print (f"C/pc: {self.pc.prev():10} {addr2track(self.pc.prev()):2} {addr2sector(self.pc.prev()):2}")

    def render_ir(self):
        d = disassemble_instr(self.ir.val())
        console.put_string(f"R/ir: {render_disassembly(d)}")

    def render_operand(self):
        if self.ir.val() is not None:
            operand = self.mem.read(instr2operand_addr(self.ir.val()))
            d = disassemble_instr(operand)
            console.put_string(f"Oprd: {render_disassembly(d)}")
        else:
            console.put_string(f"Oprd:       None")

    def render_ac(self):
        d = disassemble_instr(self.ac.val())
        console.put_string(f"A/ac: {render_disassembly(d)}")

    def render_switches(self):
        console.put_string(f"BrPt: {self.switches:10}")
        console.put_string(f"TrCS: {self.tcs_switch:>10}")
        pass

    def render_state(self):
        self.render_pc()
        self.render_ir()
        self.render_operand()
        self.render_ac()
        self.render_switches()
        
    def show_pending(self):
        if (self.run_mode == RUN_MODE_STEP) or (self.run_mode == RUN_MODE_TRACE):
            self.render_state()
        else:
            pass

    def show_result(self, result):
        if (self.run_mode == RUN_MODE_STEP) or (self.run_mode == RUN_MODE_TRACE):
            if result == STEP_CONTINUE:
                console.put_string('Result: CONTINUE')
            elif result == STEP_HALT:
                console.put_string('Result: HALT')
            else:
                console.put_string('Internal error - Instruction returned unknown result')
        elif self.run_mode == RUN_MODE_RUN:
            pass
    
    def show_changes(self):
        # last accesssed memory location only, and only if changed
        if (self.run_mode == RUN_MODE_STEP) or (self.run_mode == RUN_MODE_TRACE):
            if self.mem.val() != self.mem.prev():
                addr_string = f"{self.mem.addr():4} {addr2track(self.mem.addr()):2} {addr2sector(self.mem.addr()):2}" if self.mem.addr() is not None else 'None'
                val_string = f"{self.mem.val():10} {value2sex(self.mem.val())} {self.mem.val():08x}" if self.mem.val() is not None else 'None'
                prev_string = f"{self.mem.prev():10} {value2sex(self.mem.prev())} {self.mem.prev():08x}" if self.mem.prev() is not None else 'None'
                console.put_string(f"{addr_string:>16} {prev_string} --> {val_string}")
        else:
            pass

    def fetch(self):
        pc_val = self.pc.read()
        if pc_val is not None:
            if LGP30_MIN_ADDR <= pc_val <= LGP30_MAX_ADDR: 
                self.ir.write(self.mem.read(pc_val))
                self.pc.write(pc_val + 1)
            else:
                console.put_string(f"Illegal C/pc: {pc_val} - Cannot fetch")
                self.ir.write(None)
        else:
            console.put_string("None C/pc - Cannot fetch")
            self.ir.write(None)
        
    def execute(self):
        if self.ir.val() is not None:
            try:
                return self.operations[instr2opcode(self.ir.val())]()
            except Exception as e:
                console.put_string(f"{type(e).__name__}, {str(e)} at C/pc = {self.pc.prev()}")
                sys.exit(1)
        else:
            return STEP_HALT

    def step(self, run_mode):
    # "step" (first)
    #   fetch + inc (pc is incremented)
    #   show (previous pc, current ir)
    # "step" (next)
    #   execute (curent instruction)
    #   show_changes (previous to current)
    #   fetch + inc (pc is incremented)
    #   show (previous pc, current ir)
    #   loop
        self.run_mode = run_mode
        if self.first_step:
            self.first_step = False
            self.fetch()
            self.show_pending()
            if self.ir.val() is not None:
                return STEP_CONTINUE
            else:
                console.put_string('None R/ir - nothing to execute')
                return STEP_HALT
        else:
            if self.ir.val() is not None:
                result = self.execute()
                self.show_changes()
                self.show_result(result)
                self.fetch()
                self.show_pending()
                return result
            else:
                console.put_string('None R/ir - nothing to execute')
                self.show_pending()
                return STEP_HALT
