#ai code for testing
from common.car_db import CarDB, car_snapshot_dtype
import numpy as np
from plots.plot_functions import plot_coolant_data

# Create a mock CarDB with test data
n_snapshots = 10
car_db = CarDB(n_snapshots)

# Populate the CarDB with mock data
for i in range(n_snapshots):
    car_db._db[i]["time"]["time_since_startup"] = i * 1000  # Time in ms
    car_db._db[i]["dynamics"]["coolant_temps"][0] = 70 + i  # Coolant temp sensor 1
    car_db._db[i]["dynamics"]["coolant_temps"][1] = 65 + i  # Coolant temp sensor 2
    car_db._db[i]["dynamics"]["coolant_flow"] = 1.5 + (i * 0.1)  # Coolant flow


# Call the function to plot the data
plot_coolant_data(car_db)