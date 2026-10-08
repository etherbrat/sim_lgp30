; sim_test2.asm
; test non-arithmetic instructions
; r, u, z
start:
b word1 ; initialise A/ac with a recognisable pattern
r subend ; patch the return instruction
u subroutine ; jump to subroutine
z 0 ; stop
.locn 1000
subroutine:
b word2 ; set A/ac to a different recognisable pattern
subend:
u 0 ; patched instruction will return to caller
.locn 1100
word1: .word 0xf0f0f0f0 ; pattern 1
word2: .word 0x0f0f0f0f ; pattern 2
.end start
