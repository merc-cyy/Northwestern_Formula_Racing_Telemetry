import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum, auto
from analysis.common.parsers.telem.bit_buffer import *


# Token definitions
class TelemTokenType(Enum):
    TT_OPTION_PREFIX = auto()  # "!!"
    TT_BOARD_PREFIX = auto()  # ">"
    TT_MESSAGE_PREFIX = auto()  # ">>"
    TT_SIGNAL_PREFIX = auto()  # ">>>"
    TT_ENUM_PREFIX = auto()  # ">>>>"
    TT_IDENTIFIER = auto()
    TT_HEX_INT = auto()
    TT_INT = auto()
    TT_FLOAT = auto()
    TT_EOF = auto()


@dataclass
class TelemToken:
    type: TelemTokenType
    text: str
    data: Union[int, float, str]


# TokenReader: reads raw words
class TelemTokenReader:
    def __init__(self, config_str: str):
        self._content = config_str
        self._pos = 0
        self._n = len(config_str)

    def peekNextWord(self, max_len: int = 256) -> Optional[str]:
        pos = self._pos
        while pos < self._n and self._content[pos].isspace():
            pos += 1
        if pos >= self._n:
            return None
        start = pos
        while pos < self._n and not self._content[pos].isspace():
            pos += 1
        return self._content[start:pos]

    def moveWord(self, step: int = 1) -> bool:
        for _ in range(step):
            while self._pos < self._n and self._content[self._pos].isspace():
                self._pos += 1
            if self._pos >= self._n:
                return False
            while self._pos < self._n and not self._content[self._pos].isspace():
                self._pos += 1
        return True

    def eatUntil(self, char: str) -> bool:
        while self._pos < self._n and self._content[self._pos] != char:
            self._pos += 1
        return self._pos < self._n

    def end(self):
        self._pos = self._n


# Tokenizer: produces TelemTokens
class TelemTokenizer:
    def __init__(self, reader: TelemTokenReader):
        self.reader = reader
        self._peeked: Optional[TelemToken] = None

    def start(self) -> bool:
        return True

    def end(self):
        self.reader.end()

    def peek(self) -> TelemToken:
        if not self._peeked:
            self._peeked = self.next()
        return self._peeked

    def next(self) -> TelemToken:
        if self._peeked:
            tok, self._peeked = self._peeked, None
            return tok
        word = self.reader.peekNextWord()
        if word is None:
            return TelemToken(TelemTokenType.TT_EOF, "", "")
        # Determine token type
        if word == "!!":
            tok_type = TelemTokenType.TT_OPTION_PREFIX
        elif word == ">>>>":
            tok_type = TelemTokenType.TT_ENUM_PREFIX
        elif word == ">>>":
            tok_type = TelemTokenType.TT_SIGNAL_PREFIX
        elif word == ">>":
            tok_type = TelemTokenType.TT_MESSAGE_PREFIX
        elif word == ">":
            tok_type = TelemTokenType.TT_BOARD_PREFIX
        elif re.match(r"^0[xX][0-9A-Fa-f]+$", word):
            tok_type = TelemTokenType.TT_HEX_INT
        # Float: decimal or scientific
        elif re.match(
            r"^-?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][-+]?\d+)?$", word
        ) and re.search(r"[\.eE]", word):
            tok_type = TelemTokenType.TT_FLOAT
        elif re.match(r"^-?\d+$", word):
            tok_type = TelemTokenType.TT_INT
        else:
            tok_type = TelemTokenType.TT_IDENTIFIER
        self.reader.moveWord()
        # Parse data
        if tok_type == TelemTokenType.TT_INT:
            data = int(word, 10)
        elif tok_type == TelemTokenType.TT_HEX_INT:
            data = int(word, 0)
        elif tok_type == TelemTokenType.TT_FLOAT:
            data = float(word)
        else:
            data = word
        return TelemToken(tok_type, word, data)


# Data classes
@dataclass
class TelemEnumEntry:
    name: str
    raw_value: int


@dataclass
class TelemSignalDescription:
    name: str
    data_type: str
    start_bit: int
    length: int
    factor: float
    offset: float
    is_signed: Optional[bool] = None
    endianness: Optional[str] = None
    enums: List[TelemEnumEntry] = field(default_factory=list)


@dataclass
class TelemMessageDescription:
    name: str
    message_id: int
    message_size: int
    signals: List[TelemSignalDescription] = field(default_factory=list)
    buffer_offset: int = 0


@dataclass
class TelemBoardDescription:
    name: str
    description: str = ""
    messages: List[TelemMessageDescription] = field(default_factory=list)


@dataclass
class TelemTelemetryConfig:
    options: Dict[str, Union[int, float, str]] = field(default_factory=dict)
    boards: List[TelemBoardDescription] = field(default_factory=list)


# Builder with validation
class TelemBuilder:
    MAX_MSG_ID = 0x7FF

    def __init__(self, tokenizer: TelemTokenizer):
        self._tokenizer = tokenizer
        self._config = TelemTelemetryConfig()
        self._seen_boards = set()
        self._seen_ids = set()

    def build(self) -> TelemTelemetryConfig:
        if not self._tokenizer.start():
            raise RuntimeError("Tokenizer failed to start")
        # Global options
        while self._tokenizer.peek().type == TelemTokenType.TT_OPTION_PREFIX:
            self._parse_global_option()
        # Boards
        saw_board = False
        while self._tokenizer.peek().type == TelemTokenType.TT_BOARD_PREFIX:
            saw_board = True
            self._parse_board()
        if not saw_board:
            raise ValueError("No board defined")
        self._tokenizer.end()
        return self._config

    def _parse_global_option(self):
        self._tokenizer.next()
        name_tok = self._tokenizer.next()
        val_tok = self._tokenizer.next()
        self._config.options[name_tok.data] = val_tok.data
        self._tokenizer.reader.eatUntil("\n")

    def _parse_board(self):
        self._tokenizer.next()
        name_tok = self._tokenizer.next()
        board_name = name_tok.data
        if board_name in self._seen_boards:
            raise ValueError(f"Duplicate board '{board_name}'")
        self._seen_boards.add(board_name)
        board = TelemBoardDescription(name=board_name)
        self._config.boards.append(board)
        self._tokenizer.reader.eatUntil("\n")
        saw_msg = False
        while self._tokenizer.peek().type == TelemTokenType.TT_MESSAGE_PREFIX:
            saw_msg = True
            self._parse_message(board)
        if not saw_msg:
            raise ValueError(f"Board '{board_name}' without messages")

    def _parse_message(self, board: TelemBoardDescription):
        self._tokenizer.next()
        name_tok = self._tokenizer.next()
        id_tok = self._tokenizer.next()
        size_tok = self._tokenizer.next()
        try:
            msg_id = int(id_tok.text, 0)
        except Exception:
            raise ValueError(f"Expected message ID, got '{id_tok.text}'")
        if msg_id > self.MAX_MSG_ID:
            raise ValueError(f"Message ID {hex(msg_id)} out of range")
        if msg_id in self._seen_ids:
            raise ValueError(f"Duplicate message ID {hex(msg_id)}")
        self._seen_ids.add(msg_id)
        try:
            msg_size = int(size_tok.text, 0)
        except Exception:
            raise ValueError(f"Expected message size, got '{size_tok.text}'")
        message = TelemMessageDescription(
            name=name_tok.data, message_id=msg_id, message_size=msg_size
        )
        board.messages.append(message)
        self._tokenizer.reader.eatUntil("\n")
        saw_sig = False
        sig_names = set()
        while self._tokenizer.peek().type == TelemTokenType.TT_SIGNAL_PREFIX:
            saw_sig = True
            sig = self._parse_signal(message)
            if sig.name in sig_names:
                raise ValueError(
                    f"Duplicate signal '{sig.name}' in message '{message.name}'"
                )
            sig_names.add(sig.name)
            message.signals.append(sig)
        if not saw_sig:
            raise ValueError(f"Message '{message.name}' without signals")

    def _parse_signal(self, message: TelemMessageDescription) -> TelemSignalDescription:
        self._tokenizer.next()
        name_tok = self._tokenizer.next()
        type_tok = self._tokenizer.next()
        sb_tok = self._tokenizer.next()
        ln_tok = self._tokenizer.next()
        fac_tok = self._tokenizer.next()
        off_tok = self._tokenizer.next()
        try:
            sb = int(sb_tok.text, 0)
            ln = int(ln_tok.text, 0)
            fac = float(fac_tok.text)
            off = float(off_tok.text)
        except Exception as e:
            raise ValueError(f"Malformed signal fields for '{name_tok.data}': {e}")
        if sb + ln > message.message_size * 8:
            raise ValueError(
                f"Signal '{name_tok.data}' overruns message '{message.name}'"
            )
        sig = TelemSignalDescription(
            name=name_tok.data,
            data_type=type_tok.data,
            start_bit=sb,
            length=ln,
            factor=fac,
            offset=off,
        )
        # signedness
        nxt = self._tokenizer.peek()
        if nxt.type == TelemTokenType.TT_IDENTIFIER and nxt.data in (
            "signed",
            "unsigned",
        ):
            sig.is_signed = nxt.data == "signed"
            self._tokenizer.next()
        # endianness
        nxt = self._tokenizer.peek()
        if nxt.type == TelemTokenType.TT_IDENTIFIER and nxt.data in ("little", "big"):
            sig.endianness = nxt.data
            self._tokenizer.next()
        self._tokenizer.reader.eatUntil("\n")
        enum_vals = set()
        while self._tokenizer.peek().type == TelemTokenType.TT_ENUM_PREFIX:
            enum = self._parse_enum()
            if enum.raw_value in enum_vals:
                raise ValueError(
                    f"Duplicate enum {enum.raw_value} in signal '{sig.name}'"
                )
            enum_vals.add(enum.raw_value)
            sig.enums.append(enum)
        return sig

    def _parse_enum(self) -> TelemEnumEntry:
        self._tokenizer.next()
        name_tok = self._tokenizer.next()
        val_tok = self._tokenizer.next()
        self._tokenizer.reader.eatUntil("\n")
        try:
            rv = int(val_tok.text, 0)
        except Exception:
            raise ValueError(f"Malformed enum value '{val_tok.text}'")
        return TelemEnumEntry(name=name_tok.data, raw_value=rv)


# Data parser unchanged
@dataclass
class TelemDataParser:
    config: TelemTelemetryConfig

    def __post_init__(self):
        off = 0
        for b in self.config.boards:
            for m in b.messages:
                m.buffer_offset = off
                off += 64
        self.total_bits = off

    def parse_snapshot(self, buffer) -> Dict[str, float]:
        res = {}
        for b in self.config.boards:
            for m in b.messages:
                for s in m.signals:
                    h = TelemBitBufferHandle(
                        offset=m.buffer_offset + s.start_bit, size=s.length
                    )
                    data = buffer.read(h)
                    if data is None:
                        continue
                    signed = (
                        s.is_signed
                        if s.is_signed is not None
                        else s.data_type.startswith("int")
                    )
                    bo = s.endianness or "little"
                    raw = int.from_bytes(data, byteorder=bo, signed=signed)
                    res[f"{b.name}.{m.name}.{s.name}"] = raw * s.factor + s.offset
        return res
