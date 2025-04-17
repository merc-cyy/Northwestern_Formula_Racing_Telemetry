from analysis.common.parser_registry import (
    ParserRegistry
)
import argparse

DEFAULT_OUT = "out"

def main():
    parser = argparse.ArgumentParser(
        description="Analysis CLI Tool for NFR25"
    )

    parser.add_argument(
        "--in", type=str, help="The path for the data file to parse"
    )

    parser.add_argument(
        "--out", default=DEFAULT_OUT, type=str, help="The output path for the generated graphs"
    )

    args = parser.parse_args()

    ParserRegistry.load_parsers()
    parser_types = ParserRegistry.get_parser_versions()
    # print out all the parsers
    print(f"Found {len(parser_types)} parsers!")
    
    for pt in parser_types:
        print(f"- {pt.schema_name} v{pt.version}")
        


if __name__ == "__main__":
    main()