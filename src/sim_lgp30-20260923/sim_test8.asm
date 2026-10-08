; sim_test8.asm
; test arithmetic instructions
; n
start:
; n multiply 
b val1 ; get a value
n val2 ; shift
h out1 ; 12345 at q = 14
b val3 ; get a value
m val4 ; m multiply
h out1 ; top of 7006652 at q = 42
b val3 ; get again
n val4 ; bottom of 7006652 at q = 42 - eatqexam 3000 42
b val5 ; get a value
m val6 ; m multiply
h out1 ; top of -0.00053646432 at q=35
b val5 ; get again
n val6 ; bottom of -0.00053646432 at q=35 - eatqexam 3000 35
z 0
;
.locn 2000
val1: .atq 12345 18
val2: .lshn 4 ; right shift 4 places
val3: .atq 1234 20
val4: .atq 5678 22
val5: .atq -0.009876 17
val6: .atq 0.05432 18
;
.locn 3000
out1: .word 0
;
.end start
