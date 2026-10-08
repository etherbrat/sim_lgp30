; prog1.asm
; Programming Class Notes, Section V, Simple Problem
;
; Compute K * (F + G - J) / W
; F in 1500 at q = 7  23      -17.5
; G in 1501 at q = 7  6.375   -6.375
; J in 1502 at q = 7  15.8    -15.8
; K in 1503 at q = 7  3.142   6.284
; W in 1504 at q = 7  2.718   -10
; Result              15.6927 5.0743
;
.locn 1000
;
start:
    b F         ; F at q = 7
    a G         ; F + G at q = 7
    h temp
    s J         ; F + G - J at q = 7
    h temp
    m K         ; (F + G - J) * K
    h temp
    d W         ; (F + G -J) * K / W
    h result
    z 0
;
.locn 1500
;
F: .word 0      ; use atqdeposit
G: .word 0      ; use atqdeposit
J: .word 0      ; use atqdeposit
K: .word 0      ; use atqdeposit
W: .word 0      ; use atqdeposit
;
result: .word 0 ; use atqexamine
temp:   .word 0 ; debugging only
;
.end start
