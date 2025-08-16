# Northwestern Formula Racing Organization

## Authors
- Mercy Muiruri
- Evan Bertis-Sample

## Data Acquisition Interface Team

### Background
Every year, Northwestern University has a Formula Organization that makes an actual **Formula One** car from scratch and races the car at an annual collegiate race.

My team was the Data Acquisition-Interface team. Our role was to collect all the data coming from the **80** sensors on the car, aggregate it and visualize it for the engineering teams and later on for final competitions.

This repository contains:
1. the code to map the analog data from car sensors to a Python relational database.
2. our frontend visualization interface that represented data from the database.


### Challenges faced
One of the main challenges when building this project was that we had so much data coming in from the car and it was all in a stream of 1s and 0s. We also had many drive days (one linked here!) and each drive of the car, produced thousands of rows of data.

It was difficult for people who were not involved in the actual hardware engineering of the sensors to work with that data since it kept on changing and it was completely unreadable from a human's perspective. We needed to find a way to stream this data into a standardized schema to be used in our visualization interface.


### Solution and Technical Skills demonstrated
With guidance from upperclassmen, I used the following technical skills to build a low-level OS layer that converted the binary data to a SQL relational database.
- _Command-line scripts_: Implemented CLI commands to batch process of raw binary telemetry logs
- _File Iteration & Parsing_: Loops through all binary log files within a specified directory, reading byte-level sensor data streams.
- _Schema Mapping_: Applied a predefined SQL schema to map raw bytes to their corresponding sensor measurements (e.g., brake pressure, RPM, temperature).
- _Analog-to-Digital Interpretation_: Interpreted continuous analog sensor signals, which were digitized and stored in binary format, into human-readable engineering units.
- _Structured CSV Output_: Converted the parsed and mapped binary data into tabular CSV format, maintaining time-series alignment for each sensor channel.

# Technical Guide
daq-analysis-25
NFR25 Vehicle Analysis 

## Installation

1. Clone this repo

```sh
git clone https://github.com/nu-formula-racing/daq-analysis-25
```

2. Create and active a python virtual enviornment

```sh
python -m venv venv
source venv/Scripts/Activate
pip install -r requirements.txt
```

3. Enjoy!

## Transforming Data
Copy your log files into a directory (like data), then run the command:
```sh
python daq.py transform <data_dir> <output_dir>
```
For example:
```
python daq.py transform data out
```

## Plotting Data
Our files are organized in one folder (currenlty called 'out' but you can use the transform command to convert binary files to csv and use that folder instead)

The main function is:
```sh
python daq.py plot <data_dir> <output_dir> --driveday <driveday_dir> --logfile <name_of_log_file>
```
Note: the --driveday and --logfile are optional. Please use them to specify the specific driveday files you want or logfiles.

- Specifying driveday only means it saves a folder i.e driveday_1/ which has around ~31 plot_fn *plot function* files per log file.
- Specifying driveday and logfile means it saves a folder i.e output/log_161 which has only 31 files for all plots.
- Specifying none means you will get a folder i.e output/ with as many folders as drivedays each with subfolders for each logfile each with ~31 plots
- Use the *python daq.py list_files --driveday* to see what data files are available so you can plot them out.

## Adding Data
You can add more data from the car by uploading the binary files then transforming them to csvs and in the app.py file change DATA_DIR to the new directory of transformed files.

## Design Choices
- From the results of the *Graph Please* form, we decided to plot out every plot_function for every file since we don't know which file the user might be interested in.

Naming convention: brakepressurevtime.html (one plotted file)

- The files are html since we wanted the interactivity of plotly graphs. Thus they can only be opened in a browser or using VS Code's Live Server option[⌘ L ⌘ O] or [Alt L Alt O]

- In case you don't want to download the plots, you are welcome to use the visual interface. (Described below:)


## Deployment
Currently deployed using streamlit with continuous integration from:
 https://github.com/merc-cyy/daq-analysis-25 *(fork of https://github.com/NU-Formula-Racing/daq-analysis-25)*


## Visual interface 

#### Local setup
- Fork this repo
- Install streamlit 
```sh
pip install streamlit
```
- Run this command in root directory
```sh
streamlit run app.py
```

#### Live website
https://nfr25interface.streamlit.app/ 



   
