.locn 4032      ; (Track 63, Sector 00)
;
start:
    p   0       ; start reader
    i   0       ; get a word
    c   exec    ; word goes to memory, clear A/ac
    p   0       ; start reader
    i   0       ; get a word
;
exec:
    .word 0     ; word goes here for execution
;
; loop instruction loads here
; secondary boot loads next
;
.end start
