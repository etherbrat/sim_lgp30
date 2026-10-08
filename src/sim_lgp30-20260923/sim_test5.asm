; sim_test5.asm
; test arithmetic instructions
; s
; Failures may be due to binary conversion of decimal numbers
; or may be due to the corner cases of max numbers
; Conclusion: Tentatively good enough
;
start:
b val1 ; get a value
s val2 ; a simple subtraction
h out1 ; -6 at q = 7
b val1 ; get a value
s val3 ; another simple subtraction
h out1 ; 80 at q = 7
b val4 ; get a value
s val5 ; should overflow - does
b val5 ; get a value
s val4 ; should overflow - *** doesn't ***
b val5 ; get a value
s val14 ; should overflow - *** does ***
b val6 ; get a value
s val7 ; should overflow - *** does***
b val6 ; get a value
s val8 ; should overflow - *** does ***
b val9 ; get a value
s val10 ; should overflow - *** doesn't ***
b val9 ; get a value
s val15 ; should overflow - *** does ***
z 0

.locn 2000
val1: .atq 37 7
val2: .atq 43 7
val3: .atq -43 7
val4: .atq 0.5 0
val5: .atq -0.5 0
val6: .atq 0.999999 0  ; close to overflow
val7: .atq -0.000001 0  ; should tip into overflow
val8: .atq -0.0000011 0 ; should definitely tip into overflow
val9: .atq -0.999999 0 ; close to overflow
val10: .atq 0.000001 0 ; should tip into overflow
val14: .atq 0.5000001 0 ; should tip into overflow
val15: .atq 0.0000011 0 ; should definitely tip into overflow

.locn 3000
out1: .word 0

.end start
