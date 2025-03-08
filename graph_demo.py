import matplotlib.pyplot as plot

x = [i for i in range(-10, 11)]
y = [i**2 for i in range(-10, 11)]

plot.plot(x, y)
plot.xlabel('x - axis')
plot.ylabel('y - axis')
plot.title('Demo graph')
plot.show()
