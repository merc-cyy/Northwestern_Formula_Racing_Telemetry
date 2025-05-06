import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def brakepressurevtime(car_db, filepath):
    """ 
    Args:
    the db with data 
    file path to save plot

    Returns:
    None

    """

    # Initialize lists to store data
    brakepressure1 = []
    brakepressure2 = []

    # Iterate through all snapshots in the CarDB
    duration = len(car_db._db)
   #print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)
        #print(snapshot)
        #time_since_startup.append(snapshot['time']['time_since_startup'])
        brakepressure1.append(snapshot['ecu']['brake_pressures'][0])
        brakepressure2.append(snapshot['ecu']['brake_pressures'][1])

    times = np.arange(0,duration,1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=[brakepressure1,brakepressure2], name="brake_pressure", mode='lines'))


    # Update layout
    fig.update_layout(
        title="Brake Pressure vs Time",
        xaxis_title="Time (ms)",
        yaxis_title="Brake Pressure",
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
    brakepressurevtime(car_db=database, filepath=arg_path)