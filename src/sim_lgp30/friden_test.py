# may require companion friden_test.txt (see code)

from sim_lgp30.lgp30_friden import Friden
from sim_lgp30.friden_constants import *
import time
import sys

import os

class CPU():
    def __init__(self):
        self.run_mode = 'run'

cpu = CPU()
friden = Friden(cpu)

# output all of the codes and check which ones work
# friden.case = CASE_LOWER
# for code in range(64):
#     if code not in [CHAR_UCASE, CHAR_LCASE]:
#         try:
#             print(code)
#             friden.put_code(code)
#             print()
#         except Exception as e:
#             print(code, type(e).__name__)

# while True:
#     code = friden.get_code()
#     if code is not None:
#         break
# friden.case = CASE_UPPER
# for code in range(64):
#     if code not in [CHAR_UCASE, CHAR_LCASE]:
#         try:
#             print(code)
#             friden.put_code(code)
#             print()
#         except Exception as e:
#             print(code, type(e).__name__)

friden.set_mode(MODE_4BIT)
while True:
    try:
        code = friden.await_code()
        print(f"Got {code}")
    except Exception as e:
        if type(e).__name__ == 'IllegalCharacterError':
            print('Non-Friden character received')
            sys.exit(0)
        elif type(e).__name__ == 'InputTimeoutError':
            print('Timed out')
            sys.exit(0)          
        else:
            print('Somthing else went wrong')
            sys.exit(0)

# friden.set_mode(MODE_6BIT)
# while True:
#     try:
#         code = friden.await_code()
#         print(f"Got {code}")
#     except Exception as e:
#         if type(e).__name__ == 'IllegalCharacterError':
#             print('Non-Friden character received')
#             sys.exit(0)
#         elif type(e).__name__ == 'InputTimeoutError':
#             print('Timed out')
#             sys.exit(0)          
#         else:
#             print('Somthing else went wrong')
#             sys.exit(0)

# friden.open('src\\sim_lgp30\\friden_test.txt')
# friden.set_mode(MODE_6BIT)
# friden.case = CASE_UPPER
# while True:
#     try:
#         code = friden.await_code()
#         friden.put_code(code)
#     except Exception as e:
#         if type(e).__name__ == 'IllegalCharacterError':
#             print('Non-Friden character received')
#             sys.exit(0)
#         elif type(e).__name__ == 'InputTimeoutError':
#             print('Timed out')
#             sys.exit(0)
#         elif type(e).__name__ == 'EOFError':
#             print('End of file')
#             sys.exit(0)
#         else:
#             print('Somthing else went wrong')
#             sys.exit(0)
