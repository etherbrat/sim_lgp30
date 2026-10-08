# A bit of belts-and-braces lower casing happens throughout.

from sim_lgp30.simulator_constants import * 

class TapeLoader():

    def sex2decimal(self, sex_string):
        digit_vals = {
            '0': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            'f': 10,
            'g': 11,
            'j': 12,
            'k': 13,
            'q': 14,
            'w': 15
            }
        # LGP30 uses lower case 'l' to represent both 'l' and '1'.
        if sex_string == self.BLANK:
            return None
        val_string = sex_string.lower().replace('l', '1')
        value = 0
        try:
            for digit in val_string:
                value = (value << 4) + digit_vals[digit]
            return value
        except:
            raise IOError (f"Invalid sexadecimal character {digit} in record {self.record_index}")

    def decimal2sex(self, value):
        digit_lookup = {
            0: '0',
            1: 'l', # it's a lower case 'l'
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
        
        output = ''
        while True:
            # produce digits lsd-first
            digit_val = value & 0xf
            output = output + digit_lookup[digit_val]
            value = value >> 4
            if value == 0:
                break
        return output[::-1] # reverse them to msd-first

    def comment(self): # not authentic - added for testing purpose
        self.debug_log(f"Comment: {self.records[self.record_index]}")
        self.record_index += 1
        
    def immediate_order(self):
        # not implemented
        # consume the record
        self.record_index += 1

    def reserve(self):
        # not implemented
        # consume the record
        self.record_index += 1

    def transfer(self):
        (_, _, _, self.program_start) = self.analyse_header(self.records[self.record_index])
        self.record_index += 1

    def data_base_addr(self):
        # not impleemented
        # consume the record
        self.record_index += 1
        
    def code_base_addr(self):
        # not implemented
        # consume the record
        self.record_index += 1

    def order(self):
        # not implemented
        # consume the record
        self.record_index += 1

    def analyse_header(self, header_record):
        num_records = self.sex2decimal(header_record[1:4].lower())
        track = self.sex2decimal(header_record[4:6].lower())
        sector = self.sex2decimal(header_record[6:8].lower())
        load_address = track * self.SECTORS_PER_TRACK + sector
        self.debug_log(f"Load address: {load_address}, Track: {track}, Sector: {sector}, Num records: {num_records}")
        return (num_records, track, sector, load_address)
    
    def v_block(self):
        self.debug_log('V-block')
        header_info = self.analyse_header(self.records[self.record_index])
        load_address = header_info[self.HEADER_ADDR]
        records_remaining = header_info[self.HEADER_NUMREC]
        self.debug_log(f"Base address: {load_address}, Block size: {records_remaining}")
        self.record_index += 1 # consume the header
        # load data until and unless a header is found
        while records_remaining > 0:
            if self.record_index < len(self.records):
                current_record = self.records[self.record_index]
                if current_record is not self.BLANK:
                    if current_record[0] not in self.DISPATCH_TABLE: # meaning it's hexadecimal
                        self.debug_log(f"Current record: {current_record}")
                        value_to_load = self.sex2decimal(current_record)
                        if value_to_load & 1 != 0:
                            raise ValueError(f"Non-zero LSB in value to load at record index: {self.record_index}")
                        self.memory[load_address] = (self.sex2decimal(current_record))
                        print(f"Address: {load_address} <-- {self.memory[load_address]}")
                        load_address += 1
                        records_remaining -= 1
                        self.record_index += 1
                    else:
                        raise IOError(f"Unexpected end of v-block at record index: {self.record_index}")
                else:
                    # blank record - store zero
                    self.memory[load_address] = 0        
                    print(f"Address: {load_address} <-- 0")
                    load_address += 1
                    records_remaining -= 1
                    self.record_index += 1
            else:
                raise IOError(f"Unexpected end of file at record index: {self.record_index}")
        # run forward to next header (should come next or after checksum)
        while True:
            if self.record_index < len(self.records):
                current_record = self.records[self.record_index]
                if current_record[0] in self.DISPATCH_TABLE:
                    break
                else:
                    self.record_index += 1
            else:
                # EoF - return without bumping index
                return
        # next header - return without bumping index
        return

    def load_records(self):
        self.record_index = 0
        while self.record_index < len(self.records):
            maybe_header = self.records[self.record_index]
            self.debug_log(f"Record index: {self.record_index}, Record: {maybe_header}") 
            header_type = maybe_header[0]
            if header_type in self.DISPATCH_TABLE:
                # known type - dispatch to type handler
                self.debug_log(f"Header type {header_type} - dispatching to handler")
                self.DISPATCH_TABLE[header_type]()
            else:
                # unknown type
                raise IOError(f"Unknown header type: {maybe_header[0]}")
        # EoF
        self.debug_log('End')
        return

    def tape_to_mem(self, pathname):
        with open(pathname, 'r', encoding='utf-8') as file:
            # Read the entire text and remove all newlines
            text = file.read().replace('\n', '').replace('\r', '')
        records = []
        record_start = 0
        # Anything (including nothing) terminated by a stop char
        # is a record (either a v record or data). We convert empty
        # records into empty strings
        for index in range(len(text)):
            if text[index] == "'":
                record_end = index
                if record_start == record_end:
                    records.append(self.BLANK)
                    record_start = record_end + 1
                else:
                    records.append(text[record_start:record_end])
                    record_start = record_end + 1
        # Clean out leading dross (if any)
        self.records = [record.strip() for record in records]
        self.debug_log(f"{len(records)} records in file")
        self.load_records()
        return self.program_start
    
    def __init__(self, memory, debug_log_function):
        self.OPCODE_MASK = LGP30_OPCODE_MASK
        self.OPCODE_SHIFT = LGP30_OPCODE_SHIFT
        self.ADDRESS_MASK = LGP30_ADDRESS_MASK
        self.ADDRESS_SHIT = LGP30_ADDRESS_SHIFT
        self.TRACK_MASK = LGP30_TRACK_MASK
        self.TRACK_SHIFT = LGP30_TRACK_SHIFT
        self.SECTOR_MASK = LGP30_SECTOR_MASK
        self.SECTOR_SHIFT = LGP30_SECTOR_SHIFT
        self.SECTORS_PER_TRACK = LGP30_SECTORS_PER_TRACK
        
        self.BLANK = ''
        self.HEADER_NUMREC = 0 # header tuple index
        self.HEADER_TRACK = 1 # header tuple index 
        self.HEADER_SECTOR =2 # header tuple index
        self.HEADER_ADDR = 3 # header tuple index
        
        self.DISPATCH_TABLE = {
            '$': self.comment, # not authentic - added for testing purposes
            '+': self.immediate_order,
            ',': self.reserve,
            '.': self.transfer,
            '/': self.data_base_addr,
            ';': self.code_base_addr,
            'a': self.order,
            'b': self.order,
            'c': self.order,
            'd': self.order,
            'e': self.order,
            'h': self.order,
            'i': self.order,
            'm': self.order,
            'n': self.order,
            'p': self.order,
            'r': self.order,
            's': self.order,
            't': self.order,
            'u': self.order,
            'v': self.v_block,
            'x': self.order,
            'y': self.order,
            'z': self.order
            }
        
        self.debug_log = debug_log_function
        self.memory = memory
        self.records = None # will be intialised later
        self.record_index = None # will be initialised later
        self.program_start = None # may be discovered later
