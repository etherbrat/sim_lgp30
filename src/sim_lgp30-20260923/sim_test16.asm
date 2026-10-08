; sim_test16.py
; tests of the t instruction with and without the TCS bit set
;
; with tcs on or off
.locn 111           ; any old start address
start:
b zero              ; A <- 0
t addr1             ; should not branch
b sign_set          ; A <- sign set
t addr1             ; should branch
z 0                 ; should be skipped
;
addr1:              ; should continue here
; with tcs on
b test_instr2       ; a <- test_instr
h exec1             ; store for execution
b zero              ; a <-0
exec1:   
.word 0             ; execute test - should not branch
b test_instr2       ; a <- test instruction
a sign_set          ; set the sign bit
h exec2             ; store for execution
b zero              ; a <- 0 (should not matter)
exec2:
.word 0             ; execute test - should branch
z 60                ; should be skipped
addr2:
z 60                ; should stop here with switches off
;
.locn 3142
test_instr1:
t addr1             ; test instruction, sign bit not set
test_instr2:
t addr2             ; test instruction, sign bit may be set
zero:
.word 0             ; zero
sign_set:
.word 0x80000000    ; sign bit set
.end start
