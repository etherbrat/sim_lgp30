from msvcrt import kbhit, getch, putch

def char_available():
    return kbhit()

def get_char():
    return getch().decode('utf-8', errors='ignore')

def put_string(a_string, end='\n'):
    for char in a_string:
        putch(char.encode("utf-8"))
    if end != '':
        for char in end:
         putch(char.encode("utf-8"))
