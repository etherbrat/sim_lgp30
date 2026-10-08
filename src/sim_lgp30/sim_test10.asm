; sim_test10.asm
; non-exhaustive tests of None operand and divide by zero
.locn 1200 ; any old start address
    a   number          ; None A/ac + operand
    
.locn 1210 ; another start address
    b   number 
    a   number+1        ; A/ac + None operand
    
.locn 1220
    b number
    d CONST_0

CONST_0: .word 0        ; zero

number: .atq 1234 11    ; any old number

.end 0
