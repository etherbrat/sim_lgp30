# This is a drum EMULATOR. Storage is local and volatile.
# The intention is that the storage can be replaced
# by a physical drum, or a replica drum, under the hood.

class LGP30_Drum():

    def __init__(self):
        self.pc = None
        self.ir = None
        self.ac = None
        self.mem = {}
        
    def hard_reset(self):
        self.pc = None
        self.ir = None
        self.ac = None
        self.mem.clear() # not self.mem = {} - others have references
        
    def soft_reset(self):
        pass
        
    def registers(self):
        return {'C/pc':self.pc, 'R/ir':self.ir, 'A/ac':self.ac}

    def read_pc(self):
        return self.pc
    
    def write_pc(self, value):
        self.pc = value

    def read_ir(self):
        return self.ir
    
    def write_ir(self, value):
        self.ir = value

    def read_ac(self):
        return self.ac
    
    def write_ac(self, value):
        self.ac = value

    def read_mem(self, address):
        if address in self.mem:
            return self.mem[address]
        else:
            return None

    def write_mem(self, address, data):
        self.mem[address] = data
        
    def all_mem(self):
        return self.mem
