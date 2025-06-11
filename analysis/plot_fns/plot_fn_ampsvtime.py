import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def main(car_db, filepath):
    """ 
    Args:
    the db with data 
    file path to save plot

    Returns:
    None

    """

    # Initialize lists to store data
    gen_amps = []
    fan_amps = []
    pump_amps = []

    # Iterate through all snapshots in the CarDB
    duration = len(car_db._db)
   #print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)
        #print(snapshot)
        #time_since_startup.append(snapshot['time']['time_since_startup'])
        gen_amps.append(snapshot['pdm']['gen_amps'])
        fan_amps.append(snapshot['pdm']['fan_amps'])
        pump_amps.append(snapshot['pdm']['pump_amps'])

    times = np.arange(0,duration,1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=pump_amps, name="Pump Current", mode='lines'))
    fig.add_trace(go.Scatter(x=times, y=fan_amps, name="Fan Current", mode='lines'))
    fig.add_trace(go.Scatter(x=times, y=gen_amps, name="General Current", mode='lines'))
    
    # Update layout
    fig.update_layout(
        title="Amps vs Time",
        xaxis_title="Time (ms)",
        yaxis_title="Amps",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
       #print(f"Interactive Amps v time plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")

