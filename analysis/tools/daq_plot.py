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



def main(args):
    #use input: plot out graphs wherer out is the folder to the csv files 
    data_path = args.out#the csv files
    output_root = args.graphs#folder to save files
    plot_fn_folder = "plot_fns"#the plot fn folder is called plot_fns

    if not os.path.exists(data_path):
        print(f"Input path {data_path!r} does not exist!", file=sys.stderr)
        sys.exit(1)

    try:
        os.makedirs(output_root, exist_ok=True)#graphs
    except OSError as e:
        print(
            f"Could not create output directory {output_root!r}: {e}", file=sys.stderr
        )                                                                                                                                                                                                                                                                                                                                    
        sys.exit(1)

    # walk everything under data_path
    if os.path.isdir(data_path):#for all drive day data files
        for root, _, files in os.walk(data_path):
            for name in files:
                if name.endswith(".csv"):#process only csvs
                    src = os.path.join(root, name)#drive day data file
                    drive_day_folder = os.path.splitext(name)[0]  # e.g., 03_05_2025_drive_day_1
                    dst_dir = os.path.join(output_root,drive_day_folder)#graphs/drive-day_1 folder
                    # make sure the output subdir exists
                    os.makedirs(dst_dir, exist_ok=True)

                    plot_file(src, dst_dir, plot_fn_folder)

    elif os.path.isfile(data_path):#if there is only one drive day
        if data_path.endswith(".csv"):#ensure its a csv
            file_name_without_ext = os.path.splitext(os.path.basename(data_path))[0]
            dst = os.path.join(output_root, file_name_without_ext)
            # ensure output directory exists
            os.makedirs(dst, exist_ok=True)
            plot_file(data_path, dst, plot_fn_folder)

    else:
        print(f"Cannot read input {data_path!r}", file=sys.stderr)
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
