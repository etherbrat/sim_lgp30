# requires companion file drum_test.hex

from lgp30_drum import LGP30_Drum

DEBUG = True

def debug_log(stuff):
    if DEBUG:
        print(stuff)
    
def main():
    drum = LGP30_Drum(debug_log)
    
    drum.write_pc(777)
    drum.write_ir(888)
    drum.write_ac(999)
    drum.write_mem(1000, 555) # writes 1
    start_address = drum.hexfile_to_mem('drum_test.hex') # writes 96 (non-overlapping)
    # total written = 97
    
    print(drum.registers())
    print(len(drum.mem))
    print(drum.read_mem(1000))
    
    drum.soft_reset()
    
    print(drum.registers())
    print(len(drum.mem))
    print(drum.read_mem(1000))
    
    drum.hard_reset()

    print(drum.registers())
    print(len(drum.mem))
    print(drum.read_mem(1000))

if __name__ == '__main__':
    main()
