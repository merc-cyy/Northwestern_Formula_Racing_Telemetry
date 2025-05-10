from analysis.common.parser_registry import ParserRegistry
import argparse
import sys
import os
import importlib

DEFAULT_OUT = "out"#default out flder

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


def main():#runs in the command line
    # Path to the 'daq' directory
    daq_dir = os.path.join(os.path.dirname(__file__), TOOLS_FOLDER)#so this joins the root path to the daq directory t get full path

    # Collect all daq_*.py files
    tool_files = []#init
    # walk recursively through the daq directory to find all the tools
    # tools are python files that start with daq_
    for root, _, files in os.walk(daq_dir):#returns all the files in this folder
        for file in files:
            if file.startswith("daq_") and file.endswith(".py"):#all files starting with daq_ and ending with .py
                # get the full path to the file relative to the location of this file
                tool_path = os.path.relpath(os.path.join(root, file), daq_dir)
                tool_path = TOOLS_FOLDER + os.path.sep + tool_path#path to this file relative to daq
                tool_files.append(tool_path)#path to the files in the daq directory

    print(DAQ_ASCII_LOGO)
    print("DAQ - NFR25 Analysis Tool")#descriptive

    parser = argparse.ArgumentParser(description="Dispatcher for daq_ sub-tools.")
    subparsers = parser.add_subparsers(dest="tool", help="Sub-commands")#assigns the args to the cli to the word tool

    # Keep track of modules
    modules = {}

    # Dynamically import each sub-tool and let it register its subparser
    for tool_file in tool_files:#lop through the subpaths
        tool_name = tool_file[:-3]  # remove .py #daq_transform.py
        # Convert 'daq_foo.py' → subcommand name 'foo'
        subcommand_name = tool_name.replace("daq_", "")#remove the daq_

        # also take only the name of the tool, not the path/to/the/tool
        ## If the tool is in a subdirectory (e.g., daq/utils/daq_bar.py), we only want the final part ('bar') as the subcommand name
        subcommand_name = subcommand_name.split(os.path.sep)[-1]#bar

        # Build module path:toolname: analysis/common/daq_transform
        module_path = tool_name.replace("/", ".")#analysis.common.daq_transform
        module_path = module_path.replace("\\", ".")
        print(f"Importing module: {module_path}")#so this helps you load the files by converting the paths to modules

        # Import the modules
        module = importlib.import_module(module_path)

        # We expect each module to define a function `register_subparser`
        # to let the module configure the argparse options it needs.
        subparser = subparsers.add_parser(subcommand_name)#each funciton gets its own parser for its args


        # The module can define how it wants to configure the parser
        # e.g. add arguments, etc.
        if hasattr(module, "register_subparser"):
            module.register_subparser(subparser)#each module gets its own subparser with its own args 

        modules[subcommand_name] = module#add that module with the "key" and value is the module itself

    args = parser.parse_args()#get the user input into cli terminal

    print("")

    # If no subcommand was specified, just print help
    if not args.tool:
        parser.print_help()
        sys.exit(1)

    # Dispatch to the appropriate module’s `main` function
    # We expect each sub-tool to define a `main(args)` function
    tool_module = modules[args.tool]#get the module associated with that command
    if hasattr(tool_module, "main"):
        tool_module.main(args)#run that module with the given args. sicne we created a subparser for each module with the args it expects, you can pass in the user input
    else:
        print(f"Error: The tool {args.tool} has no main() function.")
        sys.exit(1)


if __name__ == "__main__":
    main()

    #tldr: 
    #this function handles all the cli prompts.
    # it goes through all the 'tools' which i guess could be our plot functions, assigns parsers to each (to parse the cli prompts) then stores the file as a module with that parser. 
    # All modules are stroed in a dictionary so the cli call is the key and the module is the value. 
    # Now we can just pass in the cli prompts, get respective module and call it with the user args given.
