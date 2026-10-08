from intelhex import IntelHex

import sim_lgp30.console_nonblock as console

BITS_PER_HEX = 4
HEX_MASK = 0xF
HEX_PER_WORD = 8 # 32 / BITS_PER_HEX
BYTES_PER_HEX_RECORD = 16 # on output to the hex file
LGP30_WORD_MASK = 0xffffffff # 32 bits

class HexfileLoader():

    def hexfile_to_mem(self, hexfile):
            # No validation done here. Assumed:
            # The hexfile exists
            # The hexfile contains a valid memory image
            # The hexfile contains a valid LGP-30 start address in IP, with CS = 0
            
            ih = IntelHex()
            
            try:
                ih.loadhex(hexfile)
            except:
                self.debug_log(f"Drum: Intel hex file {hexfile} - load failed")
                raise

            for (start_addr, end_addr) in ih.segments():
                self.debug_log(f"Drum: Segment byte range: {start_addr} - {end_addr}")
                # start is inclusive, end is exclusive
                # check for LGP-30 word boundaries
                if start_addr % HEX_PER_WORD == 0 and end_addr % HEX_PER_WORD == 0:
                    byte_addr = start_addr
                    # spin through the bytes in groups of HEX_PER_WORD
                    while byte_addr < end_addr:
                        mem_word = 0
                        word_addr = byte_addr // HEX_PER_WORD
                        for _ in range(HEX_PER_WORD):
                            mem_word = (mem_word << BITS_PER_HEX) + ih[byte_addr]
                            byte_addr += 1
                        if mem_word & (~LGP30_WORD_MASK):
                            console.put_string(f"Warning: Word length exceeds 32 bits at address {word_addr}")
                        if mem_word & 1 != 0:
                            console.put_string(f"Warning: Non-zero LSB at address {word_addr}")
                        self.mem[word_addr] = mem_word
                        console.put_string(f"Address: {word_addr} <-- {self.mem[word_addr]}")
                else:
                    self.debug_log(f"Drum: Intel hex file {hexfile} - segment not word-aligned")
                    return None
            try:
                program_seg = ih.start_addr['CS']
                program_start = ih.start_addr['IP']
            except:
                self.debug_log(f"Drum: Intel hex file {hexfile} - bad start address")
                raise
                
            if program_seg != 0:
                self.debug_log(f"Drum: Intel hex file {hexfile} - bad start address (non-zero CS)")
                raise ValueError()
            else:    
                self.debug_log(f"Drum: Program start address: {program_start}")
                return program_start
            
    def _words_to_bytes(self, binary_words):
        binary_bytes = {}
        for (address, data) in binary_words.items():
            byte_list = []
            for index in range(HEX_PER_WORD):
                byte_list.append(data & HEX_MASK)
                data = data >> (BITS_PER_HEX)
            # big endian
            byte_list.reverse()
            for index, byte in enumerate(byte_list):
                binary_bytes[address*HEX_PER_WORD + index] = byte
        return binary_bytes

    def _bytes_to_intel_hex(self ,binary_bytes, program_start, hexfile):
        ih = IntelHex(binary_bytes)
        ih.start_addr = {'CS':0, 'IP':program_start}
        ih.tofile(hexfile, format='hex', byte_count=BYTES_PER_HEX_RECORD)

    def mem_to_hexfile(self, hexfile, program_start):
        # No vaildation done here. Assumed:
        # The containing directory exists (the hexfile is overwritten)
        # self.mem contains a valid memory image
        # program_start is a valid LGP-30 start address
        self._bytes_to_intel_hex(self._words_to_bytes(self.mem), program_start, hexfile)

    def __init__(self, memory, debug_log_function):
        self.debug_log = debug_log_function
        self.mem = memory
