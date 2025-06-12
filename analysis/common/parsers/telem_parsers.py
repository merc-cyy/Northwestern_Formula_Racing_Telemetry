from __future__ import annotations
import struct
import numpy as np

from analysis.common.parser_registry import ParserVersion, parser_class, BaseParser
from analysis.common.car_db import CarDB
from analysis.common.parsers.telem.telem_base_parser import (
    TelemDataParser,
    DataMapper,
    YamlDataMapper
)

@parser_class(ParserVersion("NFR25", 1, 0, 0))
class TelemParserV100(TelemDataParser):
    def get_mapper(self) -> DataMapper:
        return YamlDataParser("d")