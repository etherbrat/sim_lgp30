from sim_lgp30.lgp30_atq import python2eatq, eatq2python

while True:
    value = float(input('value --> '))
    q_value = int(input('q-value --> '))
    print(f"In:  {value} at {q_value}")
    try:
        eatq_value = python2eatq(value, q_value)
    except Exception as e:
        eatq_value = 0
        print(type(e).__name__, str(e))
    eatq_value = eatq_value & 0x3fffffffffffffff
    print(f"eatq_value = {eatq_value:016x} {eatq_value:062b}")
    print(f"Out: {eatq2python(eatq_value, q_value)} at {q_value}")
