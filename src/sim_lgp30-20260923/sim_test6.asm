; sim_test6.asm
; test eatqexam command (synthetic)
start:
b bottom1 ; get the bottom half into A/ac, eatqexam top1
b bottom2 ; get the bottom half into A/ac, eatqexam top2
b bottom3 ; get the bottom half into A/ac, eatqexam top3
z 0
;
.locn 1000
top1:
.word 0b00000000000000000000000000000000; top half of 0.5 at q = 59 (incl spacer - 32 bits)
bottom1:
.word 0b00000000000000000000000000000100; bottom half of 0.5 at q = 59 (incl spacer - 32 bits)
; concetenated 62-bit value is
; 0b00000000000000000000000000000000000000000000000000000000000010 - 0.5 at q = 59 (no spacer bits - 62 bits)
;
top2: 
.word 0b00000000000000000000001010111100 ; top half of 11203 at q = 35 (incl spacer - 32 bits)
bottom2:
.word 0b00011000000000000000000000000000 ; bottom half of 11203 at q = 35 (incl spacer - 32 bits)
; concatenated 62-bit value is
; 0b00000000000000000000001010111100001100000000000000000000000000 - 11203 at q = 35 (no spacer bits - 62 bits)
;
top3:
.word 0b11111111111111111111111111110010 ; top half of -6.5 at q = 30 (incl spacer - 32 bits)
bottom3:
.word 0b10000000000000000000000000000000 ; bottom half of -6.5 at q=30 (incl spacer - 32 bits)
; concatenated 62-bit value is
; 0b11111111111111111111111111110011000000000000000000000000000000 - -6.5 at q=30 (no spacer bits - 62 bits)
;
.end start
