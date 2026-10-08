; sim_test9.asm
; test arithmetic instructions
; d
start:
b val1 ; get value
d val3 ; pos / pos ; 0.52630457 at q=0
h out1 ; store for evaluation
b val2 ; get value
d val3 ; neg / pos
h out1
b val1 ; get value
d val4 ; pos / neg
h out1
b val2 ; get value
d val4 ; neg / neg
h out1
b val3 ; get value
d val1 ; pos / pos - should overflow
b val3 ; get value
d val2 ; pos / neg - should overflow
b val4 ; get value
d val1 ; neg / pos - shold overflow
b val4 ; get value
d val2 ; neg / neg - should overflow
z 0
;
.locn 2000
val1: .atq 12345 18
val2: .atq -12348 18
val3: .atq 23456 18
val4: .atq -23456 18
;
.locn 3000
out1: .word 0
;
.end start
