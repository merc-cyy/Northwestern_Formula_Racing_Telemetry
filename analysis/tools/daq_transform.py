from analysis.common.parser_registry import ParserRegistry
from analysis.common.car_db import CarDB

import os
import sys


def register_subparser(subparser):#takes in the cli args
    subparser.add_argument(
        "input", type=str, help="The path or directory of the data files"
    )
    subparser.add_argument("out", type=str, help="The directory to store the output")


def transform_file(input_path: str, output_path: str):
    # make sure the output sub‐directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)#create the output folder

    print(f"Transforming {input_path!r} → {output_path!r}")
    db = ParserRegistry.parse(input_path) #parse the binary data and store into db
    if db == None:
        print(f"Something went wrong while parsing {input_path!r}")
        return

    db.to_csv(output_path)#write db to csv


def main(args):
    data_path = args.input
    output_root = args.out

    if not os.path.exists(data_path):
        print(f"Input path {data_path!r} does not exist!", file=sys.stderr)
        sys.exit(1)

    try:
        os.makedirs(output_root, exist_ok=True)
    except OSError as e:
        print(
            f"Could not create output directory {output_root!r}: {e}", file=sys.stderr
        )
        sys.exit(1)

    # walk everything under data_path
    if os.path.isdir(data_path):#if the data is a folder
        for root, _, files in os.walk(data_path): #go into all files
            for name in files:
                src = os.path.join(root, name)
                # path under the input root
                rel = os.path.relpath(src, data_path)
                # change extension to .csv
                rel_csv = os.path.splitext(rel)[0] + ".csv"#corresponding csv file
                dst = os.path.join(output_root, rel_csv)#path to this file

                # make sure the output subdir exists
                os.makedirs(os.path.dirname(dst), exist_ok=True)#create the output csv file

                transform_file(src, dst)#transform all binary files one by one to csv

    elif os.path.isfile(data_path):#else if tis just one file, just transform it.
        # change basename to .csv
        base_csv = os.path.splitext(os.path.basename(data_path))[0] + ".csv"
        dst = os.path.join(output_root, base_csv)

        # ensure output directory exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        transform_file(data_path, dst)

    else:
        print(f"Cannot read input {data_path!r}", file=sys.stderr)
        sys.exit(1)#error catching
