from analysis.common.parser_registry import ParserRegistry
import argparse
import sys
import os
import importlib

DEFAULT_OUT = "out"

TOOLS_FOLDER = "analysis/tools"

DAQ_ASCII_LOGO = """
            EFFFFE            
         FFFFFFFFFFFE         
      FFFFFFFFFFFFFFFFFF      
   FFFFFFFFFFFFFFFFFFFFFFFF   
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFE
FFFFFFFFM  IFFFFFFFFFFFFFFEDDD
FFFFFW      IFFFFFFFFFFEDDDDDD
FFJ    FG  ZFFFFFFFGHIJJIHFDDD
Z   PFFFP  FFGV               
 YFFFFFF        XFDDDDDDDDDDDT
FFFFFFFFFJIFDDDDDDDDDDDDDDDDDD
FFFFFFEDDDDDDDDDDDDDDDDDDDDDDD
FFFDDDDDDDDDDDDDDDDDDDDDDDDDDD
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
   DDDDDDDDDDDDDDDDDDDDDDDD   
      DDDDDDDDDDDDDDDDDD      
         CDDDDDDDDDDD         
            CDDDDC            
"""


def main():
    # Path to the 'daq' directory
    daq_dir = os.path.join(os.path.dirname(__file__), TOOLS_FOLDER)

    # Collect all daq_*.py files
    tool_files = []
    # walk recursively through the daq directory to find all the tools
    # tools are python files that start with daq_
    for root, _, files in os.walk(daq_dir):
        for file in files:
            if file.startswith("daq_") and file.endswith(".py"):
                # get the full path to the file relative to the location of this file
                tool_path = os.path.relpath(os.path.join(root, file), daq_dir)
                tool_path = TOOLS_FOLDER + os.path.sep + tool_path
                tool_files.append(tool_path)

    print(DAQ_ASCII_LOGO)
    print("DAQ - NFR25 Analysis Tool")

    parser = argparse.ArgumentParser(description="Dispatcher for daq_ sub-tools.")
    subparsers = parser.add_subparsers(dest="tool", help="Sub-commands")

    # Keep track of modules
    modules = {}

    # Dynamically import each sub-tool and let it register its subparser
    for tool_file in tool_files:
        tool_name = tool_file[:-3]  # remove .py
        # Convert 'daq_foo.py' → subcommand name 'foo'
        subcommand_name = tool_name.replace("daq_", "")

        # also take only the name of the tool, not the path/to/the/tool
        subcommand_name = subcommand_name.split(os.path.sep)[-1]

        # Build module path: 'daq.daq_foo'
        module_path = tool_name.replace("/", ".")
        module_path = module_path.replace("\\", ".")
        print(f"Importing module: {module_path}")

        # Import the module
        module = importlib.import_module(module_path)

        # We expect each module to define a function `register_subparser`
        # to let the module configure the argparse options it needs.
        subparser = subparsers.add_parser(subcommand_name)

        # The module can define how it wants to configure the parser
        # e.g. add arguments, etc.
        if hasattr(module, "register_subparser"):
            module.register_subparser(subparser)

        modules[subcommand_name] = module

    args = parser.parse_args()

    print("")

    # If no subcommand was specified, just print help
    if not args.tool:
        parser.print_help()
        sys.exit(1)

    # Dispatch to the appropriate module’s `main` function
    # We expect each sub-tool to define a `main(args)` function
    tool_module = modules[args.tool]
    if hasattr(tool_module, "main"):
        tool_module.main(args)
    else:
        print(f"Error: The tool {args.tool} has no main() function.")
        sys.exit(1)


if __name__ == "__main__":
    main()
