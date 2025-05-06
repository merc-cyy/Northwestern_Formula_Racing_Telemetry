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
    prstrain1 = []
    prstrain2 = []
    prstrain3 = [] 
    prstrain4 = []
    speed = []

    # Iterate through all snapshots in the CarDB
    duration = len(car_db._db)
    print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)

        speed.append(snapshot['dynamics']['imu']['vel'][0])
        prstrain1.append(snapshot['corners'][0]['pr_strain'])
        prstrain2.append(snapshot['corners'][1]['pr_strain'])
        prstrain3.append(snapshot['corners'][2]['pr_strain'])
        prstrain4.append(snapshot['corners'][3]['pr_strain'])


    
    times = np.arange(0,duration,1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=speed, y=[prstrain1,prstrain2,prstrain3,prstrain4], name="pr_strain", mode='lines'))


    # Update layout
    fig.update_layout(
        title="Pull Rod Strain vs Speed",
        xaxis_title="Speed",
        yaxis_title="PR Strain",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
        print(f"Pull Rod Strain vs Speed plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")