; sim_test0.asm
; basic opcodes and constants
; do they come in faithfully from the assembler?
; check by examining memory contents
b 0	; 0x1
b lastmem ; 
h 100 ; 0xc
c 200 ; 0xd
a 300 ; 0xe
s 400 ; 0xf
m 500 ; 0x7
n 600 ; 0x6
d 700 ; 0x5
e 800 ; 0x9
y 900 ; 0x2
r 1000 ; 0x3
u 1100 ; 0xa
t 1200 ; 0xd
z 0
z 4
z 8
z 16
z 32
z 32+16+8+4
p 0 ; 0x8
p 1
p 62
p 63
i 0 ; 0x4
.locn 1000
.word 0				; unchanged
.word 0xffffffff	; LSB is set to zero
.word 0xf0f0f0f0	; unchanged
.word 0x0f0f0f0f	; LSB is set to zero
.word 4294967295	; lsb is set to zero
.word 2147483647	; largest 2's complement positive in 32 bits - LSB is set to zero
.word -2147483648   ; largest 2's complement negative in 32 bits - unchanged
.locn 2000
.atq 0.5 0          ; 0100 0000 0000 0000 0000 0000 0000 0000
.atq 0.5 29         ; 0000 0000 0000 0000 0000 0000 0000 0010
.atq -0.5 0         ; 1100 0000 0000 0000 0000 0000 0000 0000
.atq -0.5 29        ; 1111 1111 1111 1111 1111 1111 1111 1110
.locn 4095
lastmem: .word 0
.end 0
