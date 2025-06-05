## daq-analysis-25
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
- Specifying none means you will get a folder i.e output/ with as many folders as drivedays each with subfolders for each logfile each with ~31 plots(not good). This will DEFINITELY fill up your laptop space so I dont advise it. Instead use the *python daq.py list_files --driveday* to see what data files are available so you can plot them out.

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



   