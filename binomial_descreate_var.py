import math

x_range = 6
P_A = 0.4

P_B = 1 - P_A
PDF = 0

for x in range (0, (x_range + 1)):
    val = (math.comb(x_range,x) * (P_A**x) * (P_B**(x_range-x)))
    PDF += val
    print(x, "-->", "P(X):", round(val, 4), "| F(X):", round(PDF, 4))
