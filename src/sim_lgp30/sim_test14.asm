; sim_test14.asm
; test i instruction in step and run modes
;
.locn 1234  ; any old start address
start:
p 0         ; set things in motion
i 0         ; see what comes in
.pchar *    ; indicate
u start     ; loop
.end start
