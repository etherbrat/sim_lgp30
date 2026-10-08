; sim_test7.asm
; test arithmetic instructions
; m
start:
; m multiply
b val1 ; get a pos
m val1 ; simple square
h out1
b val2 ; get a neg
m val2 ; square of negative
h out1
b val1 ; get a value
m val2 ; pos * neg
h out1
b val2 ; get a value
m val1 ; neg * pos
h out1 
b val3 ; get a value
m val4 ; shift
h out1
z 0
;
.locn 2000
val1: .atq 0.5 0
val2: .atq -0.5 0
val3: .atq 12345 14
val4: .rshm 3 ; right shift 3 places
;
.locn 3000
out1: .word 0
out2: .word 0
;
.end start
