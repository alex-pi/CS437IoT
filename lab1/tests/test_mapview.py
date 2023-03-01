import numpy as np
import matplotlib.pyplot as plt

# Generating data for the heat map
size = 50
data = np.random.choice([0, 1], size=size*size, p=[.1, .9])\
    .reshape((size, size))

# Function to show the heat map
plt.imshow(data, cmap='magma')

plt.title("Map View")
plt.show()