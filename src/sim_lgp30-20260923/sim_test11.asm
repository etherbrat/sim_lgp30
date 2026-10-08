; sim_test11.py
; testing printing of case, colour, backspace
;
.locn 1111      ; any old start address
start:      ; assumed black
.pchar #l   ; lower case
.pchar a    ; a
.pchar b    ; b
.pchar c    ; c
.pchar #u   ; upper case
.pchar a    ; A
.pchar b    ; B
.pchar c    ; C
.pchar #l   ; lower case
.pchar #c   ; assumed red
.pchar a    ; a
.pchar b    ; b
.pchar c    ; c
.pchar #u   ; upper case
.pchar a    ; A
.pchar b    ; B
.pchar c    ; C
.pchar #c   ; assumed black
.pchar #l   ; lower chase
.pchar a    ; a
.pchar b    ; b
.pchar c    ; c
.pchar #u   ; upper case
.pchar a    ; A
.pchar b    ; B
.pchar c    ; C
.pchar #b   ; back 1
.pchar #b   ; back 2
.pchar #b   ; back 3
.end start
