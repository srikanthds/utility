import math

lamda_avg = 0.8333
x_range = 5

for x in range (0, (x_range + 1)):
    val = (math.exp(-(lamda_avg)) * (lamda_avg**x)) / math.factorial(x)
    print(x, "-->", round(val, 4))
