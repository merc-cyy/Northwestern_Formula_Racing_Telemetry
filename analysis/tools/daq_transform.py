import argparse

import os
import sys

def register_subparser(subparser):
    subparser.add_argument(
        "input",
        type="str",
        help="The path/directory of the data files"
    )

    subparser.add_arguement(
        "out",
        type="str",
        help="The directory to store the output"
    )

def transform_file(file: str):
    print(f"Transforming file {file}")

def main(args):
    data_path = args.input

    if not os.path.exists(args):
        print(f"Input path {data_path} does not exist!")
        return

    # check if this is a directory or a file path
    if os.path.isdir(data_path):
        # iterate through all the the files
        for filename in os.listdir(data_path):
            f = os.path.join(data_path, filename)
            if os.path.isfile(f):
                transform_file(f)
    elif os.path.isfile(data_path):
        transform_file(data_path)
    else:
        print(f"Something went wrong trying to open input: {data_path}")