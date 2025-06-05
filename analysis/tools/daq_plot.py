from analysis.common.parser_registry import ParserRegistry
from analysis.common.car_db import CarDB
from analysis.common.car_db_utils import csv_to_db, getlen_csv

import os
import sys
import importlib


#takes in the word all 
def register_subparser(subparser):
    subparser.add_argument(
        "out", type=str, help="Use 'plot out graphs' to plot all the data we have had. Replace 'out' with the name of the folder with the TRANSFORMED DATA (i.e csv files) and 'graphs' with the name of the desired output folder"
    )
    #directory to save graphs
    subparser.add_argument("graphs", type=str, help="The directory to store the output plots")
    #drive day
    subparser.add_argument("--driveday",default=None, type=str,help="Optional: type the specific drive day files you want to plot out ")
    #log file
    subparser.add_argument("--logfile",default=None, type=str,help="Optional: type the specific log file you want to plot out")


def plot_file(input_path: str, output_path: str, plot_fn_path: str):
    """  
    Args:
        inputpath: takes in a path to  one csv representing data for one 'drive day'
                i.e  /03_05_2025_drive_day_1.csv
        outputpath: a path to a folder which iwll hold  ~31 files representing graphs drawn from the data that day.
                i.e /03_05_2025/graphs (a folder)
        plot_fn_path: a path to the folder holding all the plot functions
    Returns:
        Nothing. Just populates the outputfolder passed in.

    """
    # make sure the output sub‐directory exists
    os.makedirs(output_path, exist_ok=True)

    # load the csv file and convert to db
    print(f"Plotting {input_path!r} → {output_path!r}")
    db = csv_to_db(input_path)
    if db == None:
        print(f"Something went wrong while converting {input_path!r} to a database")
        return
    # now we have the db, we want to pass it in to every plt fn and 
    # save the image returned to a similarly_named file in a output folder(defined from the args)

    for root, _, files in os.walk(plot_fn_path):
        #plot_fn_path is the path to the plot_fns directory.
        #each file takes in a db and returns the image, so we also need to save the file to the output folder
        #NAMING CONVENTION:
            #plot_fn_coolanttempvtime

        for file in files:
            if file.startswith("plot_fn_") and file.endswith(".py"):#if its a plot_fn_XvY.py(a valid plot fn)
                
                mod_filename = file[:-3]#remove .py. Becomes: plot_fn_coolanttempvtime
                #print(f"{mod_filename} is being converted to a module")
                mod_path = os.path.join(root, file)#full path to this plot_fn
                #print(f"path to this module is {mod_path}")
                spec = importlib.util.spec_from_file_location(mod_filename, mod_path)
                if spec is None:
                    print(f"Couldnt load module {mod_filename}")
                new_module = importlib.util.module_from_spec(spec)#the module
                sys.modules[mod_filename] = new_module
                #print(f"Importing module: {mod_path}")#so this helps you load the files by converting the paths to modules

                try:
                    #import the module
                    spec.loader.exec_module(new_module)#load the module defined
                    #for every module, pass inthe db
                    if hasattr(new_module, "main"):
                        try: 
                            img_name = mod_filename.replace("plot_fn_", "")
                            img_filename = f"{img_name}.html"
                            img_filepath = os.path.join(output_path,img_filename)
                            new_module.main(db, img_filepath)#pass in the db to each plot fn and the fn will save that plt to that path 
                            
                        except Exception as e:
                            print(f"Error running plot function {mod_path}: {e}")
                    else:
                        print(f"Error: The tool {mod_path} has no main() function.")
                        sys.exit(1)

                except Exception as e:
                    print(f"Error importing module {mod_path}: {e}")

def has_subfolders(path):#check if a path has subfolders
    return any(
        os.path.isdir(os.path.join(path, entry))
        for entry in os.listdir(path)
    )




def main(args):
    #use input: plot out graphs where out is the folder to the csv files 
    #required inputs
    DATA_PATH = args.out#the csv files
    output_root = args.graphs#folder to save files

    data_paths = DATA_PATH# initially data_paths is a path to the main out(default)

    #optional
    drive_day = args.driveday#if not passed in will be None
    logfile = args.logfile

    plot_fn_folder = "plot_fns"#the plot fn folder is called plot_fns

    if not os.path.exists(data_paths):
        print(f"Input path {data_paths!r} does not exist!", file=sys.stderr)
        sys.exit(1)

    try:
        os.makedirs(output_root, exist_ok=True)#graphs output folder

    except OSError as e:
        print(
            f"Could not create output directory {output_root!r}: {e}", file=sys.stderr
        )                                                                                                                                                                                                                                                                                                                                    
        sys.exit(1)

    #if only driveday:
        #plot our files in that driveday
    #if only logfile:
        #plot out for the first occurrence of the log
    #if both, look for that log file in that drive day
    #if none, do all driveday plots(TOO LARGE!)

    # walk everything under data_paths

    if drive_day is not None and logfile is None:#plot out all files form this drive day (no logfile specified)
        #cehck if the path to driveday is actually in the out folder; if not error
        drive_day_path = os.path.join(DATA_PATH, drive_day)
        #if it is, repalce data path to path to that folder
        if os.path.isdir(drive_day_path):
            data_paths = drive_day_path
            print(f"Processing specific drive day folder: {data_paths}")
        else:
            raise FileNotFoundError(f"The folder '{drive_day}' was not found in '{DATA_PATH}'. Try the list_files function to see availablr drive-day files")
        
    elif logfile is not None and drive_day is not None:#we have the full path, Yay! Ideal
        logfile_path = os.path.join(DATA_PATH, drive_day, logfile)
        if os.path.isfile(logfile_path):
            data_paths = logfile_path
        else:
            print(f"Log file {logfile!r} not found in drive day folder {drive_day!r}.")
            sys.exit(1)

    elif logfile is not None and drive_day is None:
        print("Cannot pass in only logfile without driveday. Check list_files CLI to see names of available files")
        sys.exit(1)
    else:#both are None
        print("You have not passed in any args to driveday or the logfile. Currently proceeding to plot all functions for all files in all driveday folders.")
        print("WARNING: This will take too much memory in your laptop. Stop this operation while you still can",file=sys.stderr)
        data_paths = DATA_PATH


    #data_paths: could be a csv file(IDEAL), a folder with csv files(IDEAL), or a folder with subfolders with csv files(BAD).
    
    if os.path.isdir(data_paths) and has_subfolders(data_paths):#for all drive day data folders
        for root, _, files in os.walk(data_paths):#each folder
            for name in files:#each file
                if name.endswith(".csv"):#process only csvs
                    src = os.path.join(root, name)#drive day data file
                    drive_day_folder = os.path.splitext(name)[0]  # e.g., 03_05_2025_drive_day_1
                    dst_dir = os.path.join(output_root,drive_day_folder)#graphs/drive-day_1 folder
                    # make sure the output subdir exists
                    os.makedirs(dst_dir, exist_ok=True)
                    plot_file(src, dst_dir, plot_fn_folder)

    elif os.path.isdir(data_paths) and (not has_subfolders(data_paths)):
        for name in os.listdir(data_paths):#all csv files
            if name.endswith(".csv"):
                filepath = os.path.join(data_paths, name)
                file_name_without_ext = os.path.splitext(os.path.basename(filepath))[0]
                dst = os.path.join(output_root, file_name_without_ext)
                # ensure output directory exists
                os.makedirs(dst, exist_ok=True)
                plot_file(filepath, dst, plot_fn_folder)

    elif os.path.isfile(data_paths):#if there is only one drive day
        if data_paths.endswith(".csv"):#ensure its a csv
            file_name_without_ext = os.path.splitext(os.path.basename(data_paths))[0]
            dst = os.path.join(output_root, file_name_without_ext)
            # ensure output directory exists
            os.makedirs(dst, exist_ok=True)
            plot_file(data_paths, dst, plot_fn_folder)

    else:
        print(f"Cannot read input {data_paths!r}", file=sys.stderr)
        sys.exit(1)

"""
Intended folder structure
user input: plot out graphs
(*remember the 'out' is the data folder name and 'graphs' is the folder where we will save them. User can chose what ever names but the OUT FOLDER MUST EXIST or it errors since it can't access the data*)

plots
    plot_fn_coolantvtime.py
    plot_fn_wheelspeedvtime.py
    ...
out
    03_05_2025_drive_day_1.csv
    04_05_2025_drive_day_2.csv
    ...
graphs(created by the daq_plot)
    03_05_2025_drive_day_1
        coolantvtime.png
        wheelspeedvtime.png

"""
