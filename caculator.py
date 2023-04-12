import math

radius = 6371
height = 600
height = height / 1000
h_spherial = radius * math.acos(radius / (radius + height))
h_linear = math.sqrt(2 * radius * radius * height / (radius + height))
print(h_spherial)
print(h_linear)