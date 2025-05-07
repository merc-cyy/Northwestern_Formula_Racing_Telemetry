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
    coolanttemp1 = []
    coolanttemp2 = []
    coolantflow = []

    # Iterate through all snapshots in the CarDB
    duration = len(car_db._db)
   #print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)
        #print(snapshot)
        #time_since_startup.append(snapshot['time']['time_since_startup'])
        coolanttemp1.append(snapshot['dynamics']['coolant_temps'][0])
        coolanttemp2.append(snapshot['dynamics']['coolant_temps'][1])
        coolantflow.append(snapshot['dynamics']['coolant_flow'])

    times = np.arange(0,duration,1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=coolanttemp1, name="Coolant Temp 1", mode='lines'))
    fig.add_trace(go.Scatter(x=times, y=coolanttemp2, name="Coolant Temp 2", mode='lines'))
    fig.add_trace(go.Scatter(x=times, y=coolantflow, name="Coolant Flow", mode='lines'))

    # Update layout
    fig.update_layout(
        title="Coolant Factors vs Time",
        xaxis_title="Time (ms)",
        yaxis_title="Coolant",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
       #print(f"Interactive coolant factors vs time plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")

