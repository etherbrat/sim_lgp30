; sim_test12.asm
; extensive tests of the z instruction
; run multiple times with different switches set
.locn 500
start:
z 32 ; should continue with switch 32 (and possibly others) set
z 16 ; should continue with switch 16 (and possibly others) set
z 8 ; should continue with switch 8 (and possibly others) set
z 4 ; should continue with switch 4 (and possibly others) set
z 0 ; should halt
.end start

