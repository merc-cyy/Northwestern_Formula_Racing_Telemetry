from analysis.common.parser_registry import (
    ParserVersion, parser_class, BaseParser
)

from analysis.common.car_db import (
    CarDB
)

@parser_class(ParserVersion("FrontDAQ", 0))
class FrontDAQParser(BaseParser):
    def parse(filename : str) -> CarDB:
        pass