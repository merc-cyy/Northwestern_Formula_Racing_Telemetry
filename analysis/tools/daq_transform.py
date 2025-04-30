from analysis.common.parser_registry import ParserRegistry
from analysis.common.car_db import CarDB

import os
import sys


def register_subparser(subparser):
    subparser.add_argument(
        "input", type=str, help="The path or directory of the data files"
    )
    subparser.add_argument("out", type=str, help="The directory to store the output")


def transform_file(input_path: str, output_path: str):
    # make sure the output sub‐directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Transforming {input_path!r} → {output_path!r}")
    db = ParserRegistry.parse(input_path)

    # TODO: write `db` to output_path.
    # e.g.:
    # with open(output_path, 'w') as f:
    #     f.write(db.to_json())
    #
    # Or if you want to change the extension:
    # output_path = output_path.rsplit('.', 1)[0] + '.json'


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
    if os.path.isdir(data_path):
        for root, _, files in os.walk(data_path):
            for name in files:
                src = os.path.join(root, name)
                # get the path relative to the input root:
                rel = os.path.relpath(src, data_path)
                dst = os.path.join(output_root, rel)

                transform_file(src, dst)

    elif os.path.isfile(data_path):
        # single‐file case: keep the same filename
        dst = os.path.join(output_root, os.path.basename(data_path))
        transform_file(data_path, dst)

    else:
        print(f"Cannot read input {data_path!r}", file=sys.stderr)
        sys.exit(1)
