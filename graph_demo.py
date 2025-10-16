import matplotlib.pyplot as plot

x = [i for i in range(-10, 12)]
y = [i**2 for i in range(-10, 12)]

plot.plot(x, y)
plot.xlabel('x - axis')
plot.ylabel('y - axis')
plot.title('Demo graph')
plot.show()
