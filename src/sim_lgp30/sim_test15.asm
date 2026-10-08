; sim_test15.asm
; tests of simulator halt caused by uninitialised operands
; the following are tested: b, h, c, a, s, m, n, d, e, y, t, r, i
; the following opcodes are immune: u, p, z


.locn 200
; Cold start - A/ac isuninitialised
b   uninitialised   ; should halt
;
.locn 300
b   initialised     ; should succeed
;
.locn 400
; Cold start - A/ac isuninitialised
h   somewhere   ; should halt
;
.locn 500
b   initialised ; should succeed
h   somewhere   ; should succeed
;
.locn 600
; Cold start - A/ac isuninitialised
c   somewhere   ; should halt
;
.locn 700
b   initialised ; should succeed
c   somewhere   ; should succeed
;
.locn 800
; Cold start - A/ac isuninitialised
a   initialised ; should halt
;
.locn 900
b   initialised ; should succeed
a   uninitialised ; should halt
;
.locn 1000
b   initialised ; should succeed
a   initialised ; should succeed
;
.locn 1100
; Cold start - A/ac isuninitialised
s   initialised ; should halt
;
.locn 1200
b   initialised     ; should succeed
s   uninitialised   ; should halt
;
.locn 1300
b   initialised ; should succeed
s   initialised ; should succeed
;
.locn 1400
; Cold start    - A/ac isuninitialised
m   initialised ; should halt
;
.locn 1500
b   initialised ; should succeed
m   uninitialised ; should halt
;
.locn 1600
b   initialised ; should succeed
m   initialised ; should succeed
;
.locn 1700
; Cold start - A/ac isuninitialised
n   initialised ; should halt
;
.locn 1800
b   initialised ; should succeed
n   uninitialised ; should halt
;
.locn 1900
b   initialised ; should succeed
n   initialised ; should succeed
;
.locn 2000
; Cold start - A/ac isuninitialised
d   initialised ; should halt
;
.locn 2100
b   initialised     ; should succeed
d   uninitialised   ; should halt
;
.locn 2200
b   initialised ; should succeed
d   initialised ; should succeed (actually will overflow)
;
.locn 2300
; Cold start - A/ac isuninitialised
e   initialised ; should halt
;
.locn 2400
b   initialised     ; should succeed
e   uninitialised   ; should halt
;
.locn 2500
b   initialised ; should succeed
e   initialised ; should succeed
;
.locn 2600
; Cold start - A/ac isuninitialised
y   initialised ; should halt
;
.locn 2700
b   initialised     ; should succeed
y   uninitialised   ; should halt
;
.locn 2800
b   initialised ; should succeed
y   initialised ; should succeed
;
.locn 2900
; Cold start - A/ac isuninitialised
t   next    ; should halt
;
.locn 3000
b   initialised ; should succeed
t   next        ; should succeed
next:
;
.locn 3100
r   uninitialised   ; should halt
;
.locn 3200
r   initialised     ; should succeed
;
.locn 3300
; Cold start - A/ac isuninitialised
p   0
i   0   ; should halt on receipt of first input character
;
.locn 3400
b   initialised ; should succeed
p   0           ; should succeed
i   0           ; should succeed on receipt of input chracters
;
.locn 4000
initialised:    .atq 1 6
.locn 4001
uninitialised:  ; not initialised
.locn 4002
somewhere:      ; not initialised

