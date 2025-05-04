import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def wheel1speedvtime(car_db, filepath):
    """ 
    Args:
    the db with data 
    file path to save plot

    Returns:
    None

    """

    # Initialize lists to store data
    wheel1speed = []

    # Iterate through all snapshots in the CarDB
    duration = len(car_db._db)
   #print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)
        #print(snapshot)
        #time_since_startup.append(snapshot['time']['time_since_startup'])
        wheel1speed.append(snapshot['corners'][1]['wheel_speed'])

    times = np.arange(0,duration,1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=wheel1speed, name="Wheel_1_Speed", mode='lines'))


    # Update layout
    fig.update_layout(
        title="Wheel_1_Speed vs Time",
        xaxis_title="Time (ms)",
        yaxis_title="Wheel_1_Speed",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
       #print(f"Interactive wheel speed vs time plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")


def main(database, arg_path):
    """  
    function to be executed

    """
    wheel1speedvtime(car_db=database, filepath=arg_path)


