# requires companion hexin_test.hex

from lgp30_drum import LGP30_Drum

def debug_logger(stuff):
    pass

drum = LGP30_Drum(debug_logger)

start_address = drum.hexfile_to_mem('hexfile_in_test.hex')

print(f"Start address = {start_address}")
for key in drum.mem:
    print(f"{key}: {drum.mem[key]}")


