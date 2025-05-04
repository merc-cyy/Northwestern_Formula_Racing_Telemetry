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
    bmscell1temp = []

    # Iterate through all snapshots in the CarDB
    duration = len(car_db._db)
    print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)
        #print(snapshot)
        #times.append(snapshot['time']['second']) COMMENTING OUT THE TIMES SICNE WE DNT HAVE THAT DATA
        bmscell1temp.append(snapshot['bms']['cell_temps'][1])

    
    times = np.arange(0,duration,1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=bmscell1temp, name="BMS_Cell_Temp", mode='lines'))


    # Update layout
    fig.update_layout(
        title="BMS_Cell_Temp vs Time",
        xaxis_title="Time (ms)",
        yaxis_title="BMS_Cell_1_Temp",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
        print(f"Interactive wheel speed vs time plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")


# def main(database, arg_path):
#     """  
#     function to be executed

#     """
#     bmscell1tempvtime(car_db=database, filepath=arg_path)


