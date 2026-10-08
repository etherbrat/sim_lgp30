; sim_test4.asm
; test arithmetic instructions
; a
; Failures may be due to binary conversion of decimal numbers
; or may be due to the corner cases of max numbers
; Conclusion: Tentatively good enough
;
start:
b val1 ; get a value
a val2 ; a simple addition
h out1 ; 80 at q = 7
b val1 ; get a value
a val3 ; another simple addition
h out1 ; -6 at q = 7
b val4 ; get a value
a val4 ; 0.5 + 0.5 - should overflow - *** does ***
b val5 ; get a value
a val5 ; -0.5 + -0.5 - should overflow - *** doesn't ***
b val5 ; get a value
a val6 ; -0.5 + -0.500001 - should overflow - does
b val7 ; get a value
a val8 ; 0.999999 + 0.000001 - should overflow - *** doesn't ***
b val7 ; get a value
a val9 ; 0.999999 + 0.0000011 - should overflow - *** does ***
b val10 ; get a value
a val11 ; -0.999999 + -0.000001 - should overflow - doesn't
b val10 ; get a value
a val12 ; -0.999999 + -0.0000011 - should overflow - does
z 0

.locn 2000
val1: .atq 37 7
val2: .atq 43 7
val3: .atq -43 7
val4: .atq 0.5 0
val5: .atq -0.5 0
val6: .atq -0.500001 0 ; should tip into overflow
val7: .atq 0.999999 0  ; close to overflow
val8: .atq 0.000001 0  ; should tip into overflow
val9: .atq 0.0000011 0 ; should tip into overflow
val10: .atq -0.999999 0 ; close to overflow
val11: .atq -0.000001 0 ; should tip into overflow
val12: .atq -0.0000011 0 ; should tip into overflow

.locn 3000
out1: .word 0
out2: .word 0

.end start
