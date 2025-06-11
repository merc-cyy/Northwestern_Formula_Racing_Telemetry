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
    raw_displacement = []
    wheel_displacement = []
    speed = []

    # Iterate through all snapshots in the CarDB
    # duration = len(car_db._db)
    # print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)

        speed.append(snapshot['dynamics']['imu']['vel'][0])
        raw_displacement.append(snapshot['corners'][0]['raw_sus_displacement'])
        wheel_displacement.append(snapshot['corners'][0]['wheel_displacement'])



    
    # times = np.arange(0,duration,1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=speed, y=raw_displacement, name="Wheel 1 Raw Sus Displacement", mode='lines'))
    fig.add_trace(go.Scatter(x=speed, y=wheel_displacement, name="Wheel 1 Wheel Sus Displacement", mode='lines'))


    # Update layout
    fig.update_layout(
        title="Suspension Displacement vs Speed for Wheel 1",
        xaxis_title="Speed",
        yaxis_title="Suspension Displacement",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
        print(f"Suspension Displacement vs Speed for Wheel 1 plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")