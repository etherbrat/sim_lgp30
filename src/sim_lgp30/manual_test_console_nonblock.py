import sim_lgp30.console_nonblock as console

import time

while True:
    if console.char_available():
        my_char = console.get_char()
        console.put_string(my_char)
    else:
        time.sleep(0.1)

