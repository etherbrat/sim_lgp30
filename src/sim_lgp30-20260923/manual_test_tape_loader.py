# requires companion tape_loader_test.txt

from sim_lgp30.lgp30_tape_loader import TapeLoader

DEBUG = False

def debug_logger(stuff):
    if DEBUG:
        print(stuff)

if __name__ == '__main__':
    memory = {}
    tape_loader = TapeLoader(memory, debug_logger)
    try:
        start_address = tape_loader.tape_to_mem('tape_loader_test.txt')
        print(f"Start address: {start_address}")
        for key in memory.keys():
            track = key // 64
            sector = key - (track * 64)
            print(f"{key:4} {track:2} {sector:2} {memory[key]}")
    except Exception as e:
        print(f"{type(e).__name__}: {str(e)}")
