import matplotlib.pyplot as plt

def plot_coolant_data(car_db):
    """
    Plots coolant temperature and coolant flow versus time using data from CarDB.
    """
    # Initialize lists to store data
    time_since_startup = []
    coolant_temp_1 = []
    coolant_temp_2 = []
    coolant_flow = []

    # Iterate through all snapshots in the CarDB
    for idx in range(len(car_db._db)):
        snapshot = car_db.get_snapshot(idx)
        print(snapshot)
        time_since_startup.append(snapshot.time.time_since_startup)
        coolant_temp_1.append(snapshot.dynamics.coolant_temps[0])  # First coolant temp sensor
        coolant_temp_2.append(snapshot.dynamics.coolant_temps[1])  # Second coolant temp sensor
        coolant_flow.append(snapshot.dynamics.coolant_flow)

    # Plot coolant temperatures
    plt.figure(figsize=(10, 6))
    plt.plot(time_since_startup, coolant_temp_1, label="Coolant Temp Sensor 1", color="red")
    plt.plot(time_since_startup, coolant_temp_2, label="Coolant Temp Sensor 2", color="blue")
    plt.xlabel("Time Since Startup (ms)")
    plt.ylabel("Temperature (°C)")
    plt.title("Coolant Temperatures vs Time")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot coolant flow
    plt.figure(figsize=(10, 6))
    plt.plot(time_since_startup, coolant_flow, label="Coolant Flow", color="green", linestyle="--")
    plt.xlabel("Time Since Startup (ms)")
    plt.ylabel("Flow Rate (Binary or Units)")
    plt.title("Coolant Flow vs Time")
    plt.legend()
    plt.grid(True)
    plt.show()