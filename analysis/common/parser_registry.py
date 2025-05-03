from analysis.common.car_db import CarDB, CarSnapshot

from dataclasses import dataclass#used to generate classes that store data
from enum import Enum
import pkgutil
import importlib#both these last two are for importing modules

import analysis.common.parsers as parser_mod#this has the specific code for reading in files

#the dataclass creates some basic functions already for the ParserVersion
@dataclass(frozen=True)#frozen true means attributes cannot be changed after creation
class ParserVersion:#the blueprint for storing the version of the file
    schema_name: str#name
    version: int#the current version


def parser_class(version: ParserVersion):
    """
    A decorator for marking a class as a parser. SO it marks other classes as able to read in files
    It must inherit from BaseParser
    """

    def decorator(cls):
        ParserRegistry.add_parser(version, cls)#so it marks this class as able to read in data for this specific version
        return cls

    return decorator


class BaseParser:#this is the root class of every parser. Has the fn parse that takes in the name of the file and returns the data as organized into a Python DB
    def parse(filename: str) -> CarDB:
        pass#just a template that other more specific functions can follow


class ParserRegistry:
    parsers: dict[ParserVersion, BaseParser] = {}#a dict where the key is the version and value is the class that can read in that type of data
    loaded : bool = False

    @staticmethod#static means it belongs to only this class not all objects of this instance
    def add_parser(version: ParserVersion, cls):
        ParserRegistry.parsers[version] = cls#adds the version=>class key-value pair into our dictionary

    @staticmethod
    def get_parser(version : ParserVersion):
        return ParserRegistry.parsers.get(version, None)#gets the parser

    @staticmethod
    def get_parser_versions() -> list[ParserVersion]:
        return ParserRegistry.parsers.keys()#list of all parser versions currently saved

    @staticmethod
    def load_parsers():
        package = parser_mod#all the specific parser files
        for finder, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            #ispkg--> means its a subdirectory on its own
            #module_name --> means its the python filename
            full_module_name = f"{package.__name__}.{module_name}"#filename to import
            importlib.import_module(full_module_name)#import
        loaded = True#a boolean to say, yes we have loaded all the necessary python files

    @staticmethod
    def parse(filename : str) -> CarDB :#actual file to be parse -> cardb
        if ParserRegistry.loaded == False:#if not uyet loaded parsers
            ParserRegistry.load_parsers()#load them

        # find the parser
        # for now, just pass in the only one
        parser = ParserRegistry.get_parser(ParserVersion("FrontDAQ", 0))
        if parser == None:
            return None

        return parser.parse(filename)
    
    #tldr:
    #initialization of the parsers classes and their types and hierarchy
    #so you just pass in a file and it finds the appropriate parser for it and calls the parsign function for that data and returns the parsed data as a DB.
