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
    apps1 = []
    apps2 = []
    apps_diff = []#as a percentage out of 100%

    # Iterate through all snapshots in the CarDB
    duration = len(car_db._db)
   #print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)
        #print(snapshot)
        #time_since_startup.append(snapshot['time']['time_since_startup'])
        apps1.append(snapshot['ecu']['apps_positions'][0])
        apps2.append(snapshot['ecu']['apps_positions'][1])
        

    times = np.arange(0,duration,1)
    apps_diff = np.abs(np.subtract(np.array(apps1), np.array(apps2))) #need to convert to out of 100%

    # Find the maximum difference to scale percentages
    max_apps_diff = np.max(apps_diff)
    if max_apps_diff > 0:
        apps_diff_percentage = (apps_diff / max_apps_diff) * 100
    else:
        apps_diff_percentage = np.zeros_like(apps_diff) 
     
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=apps1, name="APPS 1", mode='lines'))
    fig.add_trace(go.Scatter(x=times, y=apps2, name="APPS 2", mode='lines'))
    fig.add_trace(go.Scatter(x=times, y=apps_diff_percentage, name="APPS diff (out of 100%)", mode='lines'))
    
    # Update layout
    fig.update_layout(
        title="APPS vs Time",
        xaxis_title="Time (ms)",
        yaxis_title="APPS",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
       #print(f"Interactive APPS vs time plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")

