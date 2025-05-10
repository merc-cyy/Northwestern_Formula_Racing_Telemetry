import plotly.graph_objects as go
from plotly.subplots import make_subplots

def main(car_db, filepath):
    """ 
    Args:
    the db with data 
    file path to save plot

    Returns:
    None

    """

    # Initialize lists to store data
    steering_angle = []
    lateral_acc = []

    # Iterate through all snapshots in the CarDB
    # duration = len(car_db._db)
    # print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)

        steering_angle.append(snapshot['dynamics']['steering_angle'])
        lateral_acc.append(snapshot['dynamics']['imu']['accel'][0])




    
    # times = np.arange(0,duration,1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=steering_angle, y=lateral_acc, name="Lateral Acceleration", mode='lines'))
    

    # Update layout
    fig.update_layout(
        title="Lateral Acceleration v Steering Angle",
        xaxis_title="Angle",
        yaxis_title="Acceleration",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
        print(f" Lateral Acc. v Steering Angle plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")