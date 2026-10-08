; sim_test1.asm
; test non-arithmetic instructions
; b, h, c, e, y
start:
b word1
c word3
b word2
h word4
b word5
e word7
b word6
e word7
b word8
y word9
z 0
.locn 1000
word1:
.word 0x10101010 ; operand for b instruction
.locn 1100
word2:
.word 0xfffffffe ; operand for b instruction
.locn 1200
word3:
.word 0 ; target for c  instruction
.locn 1300
word4:
.word 0 ; target for h instruction
.locn 1400
word5:
.word 0xf0f0f0f0 ; A/ac for e instruction
word6:
.word 0x0f0f0f0f ; A/ac for e instruction
word7:
.word 0x12481248 ; mask for e instruction
.locn 1500
word8:
b 1234 ; source of address for y instruction
.locn 1600
word9:
b 0 ; target of y instruction
.end start
