# must be run in an IDE that supports msvcrt (not Thonny)

import time
import msvcrt

def getcmd():
    print('--> ', end='')
    line = ''
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch().decode('utf-8')
            if char == '\b':
                print('\b \b', end='')
                line = line[:-1]
            elif char in ['\r', '\n']:
                print()
                return line
            elif char.isprintable():
                print(char, end='')
                line = line + char
            else:
                time.sleep(0.1)

def main():
    while True:
        cmd = getcmd()
        print(cmd)

if __name__ == '__main__':
    main()
