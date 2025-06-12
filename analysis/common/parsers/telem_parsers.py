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


# 49.48.48 because I wrote the version wrong
# I wrote it in ascii, not the raw value :/
@parser_class(ParserVersion("NFR25", 49, 48, 48))
class TelemParserV100(TelemDataParser):
    def get_mapper(self) -> DataMapper:
        return YamlDataMapper("mappings/2025_6_10.yml")