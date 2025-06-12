from analysis.common.car_db import CarDB, CarSnapshot

from dataclasses import dataclass  # used to generate classes that store data
from enum import Enum
import pkgutil
import importlib  # both these last two are for importing modules

import analysis.common.parsers as parser_mod


@dataclass(frozen=True)
class ParserVersion:
    schema_name: str
    major: int
    minor: int
    patch: int


def parser_class(version: ParserVersion):
    """
    A decorator for marking a class as a parser. SO it marks other classes as able to read in files
    It must inherit from BaseParser
    """

    def decorator(cls):
        ParserRegistry.add_parser(
            version, cls
        )  # so it marks this class as able to read in data for this specific version
        return cls

    return decorator


class BaseParser:  # this is the root class of every parser. Has the fn parse that takes in the name of the file and returns the data as organized into a Python DB
    def parse(filename: str) -> CarDB:
        pass  # just a template that other more specific functions can follow


class ParserRegistry:
    parsers: dict[ParserVersion, BaseParser] = {}
    loaded: bool = False

    @staticmethod  # static means it belongs to only this class not all objects of this instance
    def add_parser(version: ParserVersion, cls):
        print(
            f"Adding parser: {version.schema_name} ({version.major}.{version.minor}.{version.patch})"
        )
        ParserRegistry.parsers[version] = cls

    @staticmethod
    def get_parser(version: ParserVersion):
        return ParserRegistry.parsers.get(version, None)

    @staticmethod
    def get_parser_versions() -> list[ParserVersion]:
        return (
            ParserRegistry.parsers.keys()
        )  # list of all parser versions currently saved

    @staticmethod
    def load_parsers():
        package = parser_mod  # all the specific parser files
        for finder, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{package.__name__}.{module_name}"
            importlib.import_module(full_module_name)
        loaded = True

    @staticmethod
    def parse(filename: str) -> CarDB:
        """
        Detect the file’s schema + version and dispatch to the best
        parser we have registered.  Raises ValueError if no compatible
        parser is found.
        """
        if not ParserRegistry.loaded:
            ParserRegistry.load_parsers()

        # Peek at the header (≤ 9 bytes)
        PREAMBLE = b"NFR25"

        # assume the old version
        parser_name = "NFR25"
        major, minor, patch = [0, 0, 0]

        with open(filename, "rb") as fh:
            header = fh.read(len(PREAMBLE) + 3)  # 5-byte magic + 3-byte version

        if len(header) < len(PREAMBLE):
            raise ValueError("File too short to contain header")
        if not header.startswith(PREAMBLE):
            print(
                f"Unknown or unsupported file format (missing 'NFR25', got {header}), assuming NFR25 0.0.0"
            )

        major, minor, patch = header[len(PREAMBLE) : len(PREAMBLE) + 3]
        requested = ParserVersion(parser_name, major, minor, patch)

        print(f"Using Parser : {parser_name} v{major}.{minor}.{patch}")

        # Try exact match first
        parser_cls = ParserRegistry.get_parser(requested)

        # newest parser
        if parser_cls is None:
            compatible = [
                v
                for v in ParserRegistry.get_parser_versions()
                if v.schema_name == requested.schema_name
                and (v.major, v.minor, v.patch)
                <= (requested.major, requested.minor, requested.patch)
            ]
            if compatible:
                best = max(compatible, key=lambda v: (v.major, v.minor, v.patch))
                parser_cls = ParserRegistry.get_parser(best)

        if parser_cls is None:
            raise ValueError(
                f"No parser available for schema '{requested.schema_name}' "
                f"version {requested.major}.{requested.minor}.{requested.patch}"
            )

        # Try exact match first
        parser_cls = ParserRegistry.get_parser(requested)
        instance = parser_cls()
        return instance.parse(filename)
