; sim_test3.asm
; test non-arithmetic instructions
; t
start:
b negative_word
t jump1 ; should jump to jump1
z 0 ; should not stop here
jump1:
b positive_word 
t jump2 ; should not jump
z 0 ; should stop here with positive word in A/ac
jump2:
b funny_pattern ; indicates something went wrong
z 0 ; should not stop here
.locn 1234
negative_word:
.atq -0.5 0
positive_word:
.atq 6 3
funny_pattern:
.word 0xf0f0f0f0
.end start
