import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from typing import List, Dict
import tempfile


def load_dataframe(filepath: str) ->  pd.DataFrame:
    """
    Loads CSV or Excel file into Pandas DataFrame.

    Args:
    filepath: The path to the file to load.
    Returns:
        the corresponding DataFrame.
    """

    try:
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif filepath.endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            st.error(f"Unsupported file type: {filepath}")
    except Exception as e:
        st.error(f"Error loading {filepath}: {e}")
    return df




def plot_data(data: pd.DataFrame, x_axis: str, y_axes: List[str], plot_title: str, plot_type: str = "Line Plot") -> go.Figure:
    """
    Plots the data based on user selections using Plotly.  Returns the Plotly figure.

    Args:
        data: The Pandas DataFrame containing the data to plot.
        x_axis: The column name for the x-axis.
        y_axis: The column name for the y-axis.
        plot_title: Title of the plot
        plot_type: The type of plot to create ("Line Plot" or "Scatter Plot").

    Returns:
        A Plotly Figure object.
    """
    fig = go.Figure()

    for y_col in y_axes:
        if plot_type == "Line Plot":
            fig.add_trace(go.Scatter(x=data[x_axis], y=data[y_col], mode='lines', name=y_col))
        elif plot_type == "Scatter Plot":
            fig.add_trace(go.Scatter(x=data[x_axis], y=data[y_col], mode='markers', name=y_col))
        else:
            st.error(f"Unsupported plot type: {plot_type}")
            return go.Figure()
    legend=dict(
    font=dict(size=14, color="#FFFFFF"),
    bgcolor="rgba(0,0,0,0)",
    bordercolor="#4a4a4a",
    borderwidth=1)

    fig.update_layout(
        title=plot_title,
        xaxis_title=x_axis,
        yaxis_title=", ".join(y_axes),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font_color="#FFFFFF",
        xaxis=dict(gridcolor="#4a4a4a", zerolinecolor="#4a4a4a"),
        yaxis=dict(gridcolor="#4a4a4a", zerolinecolor="#4a4a4a"),
        legend=legend


        
    )
    return fig

def get_plot_download_link(fig, filename="plot.html"):
    """
    Saves a Plotly figure to an HTML file and returns a download link.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
        fig.write_html(tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            st.download_button(
                label="Downlaod Interactive Plot and Open in Browser",
                data=f,
                file_name=filename,
                mime="text/html"
            )

def main():
    """
    Main function to run the Streamlit app.
    """
   
    # Set page configuration
    st.set_page_config(
        page_title="NFR-25 DAQ Interface",
        page_icon="NFR",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Main content
    st.title("NFR 25 DAQ Interface")
    st.write("Northwestern Formula Racing's 2025 DAQ data analysis tool.")

    # Sidebar
    st.sidebar.title("Navigation")
    st.sidebar.write("Use the sidebar to select the Drive Day data.")

    # # File uploader in the sidebar for multiple files
    # uploaded_files = st.sidebar.file_uploader("Select the drive day", type=["csv", "xlsx"], accept_multiple_files=True)
    uploaded_files = None

    select_day = None
    select_csv = None 

    #Selecting the Drive Day
    DATA_DIR = 'out'#hardcoded for now
    day_folders = []#list of driveday folder paths
    for folder in os.listdir(DATA_DIR):
        if os.path.isdir(os.path.join(DATA_DIR,folder)):#if its a folder
            day_folders.append(folder)
    day_folders = sorted(day_folders)#sort the folders for easy select
    select_day = st.sidebar.selectbox('Select the Drive Day', day_folders, key='selected_day')
    #Selecting the Files
    if select_day:
        folder_path = os.path.join(DATA_DIR, select_day)#path to the selected folder
        csv_files = []#list of csv files for that day
        for file in os.listdir(folder_path):
            if file.endswith(".csv"):
                csv_files.append(file)
        select_csv = st.sidebar.selectbox("Select Data File", csv_files, key="selected_csv")

    st.sidebar.selectbox("Type of Visualizations", ["Linear", "Special"], key="selected_type")

    if st.session_state.selected_type == "Linear":
        num_plots = st.sidebar.selectbox("Number of Plots", [1, 2, 3, 4], index=1)  # default 2

        ##
        if select_csv:#if you have selected a csv
            fullfilepath = os.path.join(folder_path,select_csv )
            df = load_dataframe(filepath=fullfilepath)#load selected csv into dataframe
            df = df.reset_index(drop=False)
            df.rename(columns={'index':'Time-index'}, inplace=True)
            #timesteps


            st.write("File uploaded successfully!")
            st.write("Preview of the data:")
            st.write(df)

            plot_configs = []  # List to store plot configurations
            show_plots = False #flag

            # Create a 2x2 grid for plot input
            cols = st.columns(2)
            rows = [cols[i % 2] for i in range(num_plots)]

            for i in range(num_plots):
                with rows[i]:
                    st.subheader(f"Plot {i + 1}")
                    # Use a unique key for each selectbox
                    x_axis_key = f"x_axis_{i}"
                    y_axis_key = f"y_axis_{i}"
                    plot_type_key = f"plot_type_{i}"

                    x_axis = st.selectbox(f"Select X-axis variable for Plot {i + 1}", df.columns, key=x_axis_key)
                    y_axes = st.multiselect(f"Select Y-axis variable for Plot {i + 1}", df.columns, key=y_axis_key)
                    plot_type = st.selectbox(f"Select Plot Type for Plot {i + 1}", ["Line Plot", "Scatter Plot"], key=plot_type_key)

                    if y_axes:#only if the user has selected plotting values
                        plot_configs.append({
                            "x_axis": x_axis,
                            "y_axis": y_axes,#could be a list
                            "plot_type": plot_type,
                            "df": df, #store df
                            "title": f"{', '.join(y_axes)} vs {x_axis}"
                        })

            # Generate Plots Button
            if st.button("Generate Plots"):
                show_plots = True #set flag

            if show_plots and plot_configs:
                # Create a 2x2 grid for displaying the plots
                plot_cols = st.columns(2)
                plot_rows = [plot_cols[i % 2] for i in range(num_plots)]
                for i, config in enumerate(plot_configs):
                    with plot_rows[i]:
                        fig = plot_data(data=config["df"], x_axis=config["x_axis"], y_axes=config["y_axis"], plot_type=config["plot_type"], plot_title=config['title'])
                        st.plotly_chart(fig, use_container_width=True)
                        get_plot_download_link(fig, filename=f"plot_{i + 1}.html")
    else: #special graphs

        #Sidebar
        st.sidebar.selectbox("Choose your graph", ["Not yet supported. Contact DAQ team!"], key="selected_special_graph")


        #Main
        st.write("Non-linear graphs will be supported here!")
        st.write("If you came here by mistake, please select 'Linear' Visualization on the sidebar to go home")

        # Add a map of Northwestern University with a pin on Ford Design Center
        st.title("Welcome to Northwestern Formula Racing 2025")
        ford_design_center_coords = [42.056459, -87.675267]
        st.map(pd.DataFrame([{"lat": ford_design_center_coords[0], "lon": ford_design_center_coords[1]}]), color="#4E2A84", zoom=14)



if __name__ == "__main__":
    main()
