from analysis.common.car_db import CarDB, CarSnapshot

from dataclasses import dataclass
from enum import Enum
import pkgutil
import importlib

import analysis.common.parsers as parser_mod


@dataclass(frozen=True)
class ParserVersion:
    schema_name: str
    version: int


def parser_class(version: ParserVersion):
    """
    A decorator for marking a class as a parser.
    It must inherit from BaseParser
    """

    def decorator(cls):
        ParserRegistry.add_parser(version, cls)
        return cls

    return decorator


class BaseParser:
    def parse(filename: str) -> CarDB:
        pass


class ParserRegistry:
    parsers: dict[ParserVersion, BaseParser] = {}
    loaded : bool = False

    @staticmethod
    def add_parser(version: ParserVersion, cls):
        ParserRegistry.parsers[version] = cls

    @staticmethod
    def get_parser(version : ParserVersion):
        return ParserRegistry.parsers.get(version, None)

    @staticmethod
    def get_parser_versions() -> list[ParserVersion]:
        return ParserRegistry.parsers.keys()

    @staticmethod
    def load_parsers():
        package = parser_mod
        for finder, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{package.__name__}.{module_name}"
            importlib.import_module(full_module_name)
        loaded = True

    @staticmethod
    def parse(filename : str) -> CarDB :
        if ParserRegistry.loaded == False:
            ParserRegistry.load_parsers()

        # find the parser
        # for now, just pass in the only one
        parser = ParserRegistry.get_parser(ParserVersion("FrontDAQ", 0))
        if parser == None:
            return None

        return parser.parse(filename)
