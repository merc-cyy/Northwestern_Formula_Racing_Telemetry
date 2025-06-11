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
    brake_pressure1 = []
    brake_pressure2 = []
    long_decel = [] #longitudinal deceleration

    # Iterate through all snapshots in the CarDB
    # duration = len(car_db._db)
    # print(f"NUMBER OF RECORDS:{duration}")
    for idx in range(len(car_db._db)):#the numebr of records?
        snapshot = car_db.raw_record(idx)

        brake_pressure1.append(snapshot['ecu']['brake_pressures'][0])
        brake_pressure2.append(snapshot['ecu']['brake_pressures'][1])
        long_decel.append(snapshot['dynamics']['imu']['accel'][1])




    
    # times = np.arange(0,duration,1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=brake_pressure1, y=long_decel, name="Longitudinal Deceleration", mode='lines'))
    

    # Update layout
    fig.update_layout(
        title="Longitudinal Deceleration v Brake Pressure",
        xaxis_title="Brake Pressure",
        yaxis_title="Longitudinal Deceleration",
        template="plotly_dark",
    )

    # 3. Save the Plot as an HTML File
    try:
        fig.write_html(filepath)
        #print(f" Longitudinal Deceleration v Brake Pressure plot saved to {filepath}")
    except Exception as e:
        print(f"Error saving plot: {e}")