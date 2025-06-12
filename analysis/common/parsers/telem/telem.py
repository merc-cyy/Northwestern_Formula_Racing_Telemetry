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
    data: Union[int, float, str, None] = None


# TokenReader: reads raw words from the input
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


# Tokenizer: produces TelemToken objects from the reader
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
            tok = self._peeked
            self._peeked = None
            return tok
        word = self.reader.peekNextWord()
        if word is None:
            return TelemToken(TelemTokenType.TT_EOF, "")
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
        elif re.match(r"^0x[0-9A-Fa-f]+$", word):
            tok_type = TelemTokenType.TT_HEX_INT
        elif re.match(r"^-?\d+$", word):
            tok_type = TelemTokenType.TT_INT
        elif re.match(r"^-?\d+\.\d*([eE][-+]?\d+)?$", word):
            tok_type = TelemTokenType.TT_FLOAT
        else:
            tok_type = TelemTokenType.TT_IDENTIFIER
        self.reader.moveWord()
        data = None
        if tok_type == TelemTokenType.TT_INT:
            data = int(word)
        elif tok_type == TelemTokenType.TT_HEX_INT:
            data = int(word, 16)
        elif tok_type == TelemTokenType.TT_FLOAT:
            data = float(word)
        else:
            data = word
        return TelemToken(tok_type, word, data)


# Data classes with Telem prefix
@dataclass
class TelemEnumEntry:
    name: str
    raw_value: int


@dataclass
class TelemSignalDescription:
    name: str = ""
    data_type: str = ""
    start_bit: int = 0
    length: int = 0
    factor: float = 1.0
    offset: float = 0.0
    is_signed: Optional[bool] = None
    endianness: Optional[str] = None
    enums: List[TelemEnumEntry] = field(default_factory=list)


@dataclass
class TelemMessageDescription:
    name: str = ""
    message_id: int = 0
    message_size: int = 0
    signals: List[TelemSignalDescription] = field(default_factory=list)
    buffer_offset: int = 0  # assigned at bus construction


@dataclass
class TelemBoardDescription:
    name: str = ""
    description: str = ""
    messages: List[TelemMessageDescription] = field(default_factory=list)


@dataclass
class TelemTelemetryConfig:
    options: Dict[str, Union[int, float, str]] = field(default_factory=dict)
    boards: List[TelemBoardDescription] = field(default_factory=list)


# Builder follows C++ structure
class TelemBuilder:
    def __init__(self, tokenizer: TelemTokenizer):
        self._tokenizer = tokenizer
        self._config = TelemTelemetryConfig()
        self._current_board: Optional[TelemBoardDescription] = None
        self._current_message: Optional[TelemMessageDescription] = None
        self._current_signal: Optional[TelemSignalDescription] = None
        self._message_ids = set()

    def build(self) -> TelemTelemetryConfig:
        if not self._tokenizer.start():
            raise RuntimeError("Failed to start tokenizer")
        while True:
            tok = self._tokenizer.peek()
            if tok.type != TelemTokenType.TT_OPTION_PREFIX:
                break
            self._parse_global_option()
        saw_board = False
        while True:
            tok = self._tokenizer.peek()
            if tok.type == TelemTokenType.TT_BOARD_PREFIX:
                saw_board = True
                self._parse_board()
            else:
                break
        if not saw_board:
            raise ValueError("No board defined")
        self._tokenizer.end()
        return self._config

    def _parse_global_option(self):
        self._tokenizer.next()
        name_t = self._tokenizer.next()
        val_t = self._tokenizer.next()
        self._config.options[name_t.data] = val_t.data
        self._tokenizer.reader.eatUntil("\n")

    def _parse_board(self):
        self._tokenizer.next()
        name_t = self._tokenizer.next()
        bd = TelemBoardDescription(name=name_t.data)
        self._config.boards.append(bd)
        self._current_board = bd
        self._tokenizer.reader.eatUntil("\n")
        saw_msg = False
        while self._tokenizer.peek().type == TelemTokenType.TT_MESSAGE_PREFIX:
            saw_msg = True
            self._parse_message()
        if not saw_msg:
            raise ValueError(f"Board '{bd.name}' without messages")

    def _parse_message(self):
        self._tokenizer.next()
        name_t = self._tokenizer.next()
        id_t = self._tokenizer.next()
        sz_t = self._tokenizer.next()
        msg = TelemMessageDescription(
            name=name_t.data, message_id=id_t.data, message_size=sz_t.data
        )
        if msg.message_id in self._message_ids:
            raise ValueError(f"Duplicate message ID {msg.message_id}")
        self._message_ids.add(msg.message_id)
        self._current_board.messages.append(msg)
        self._current_message = msg
        self._tokenizer.reader.eatUntil("\n")
        saw_sig = False
        while self._tokenizer.peek().type == TelemTokenType.TT_SIGNAL_PREFIX:
            saw_sig = True
            self._parse_signal()
        if not saw_sig:
            raise ValueError(f"Message '{msg.name}' without signals")

    def _parse_signal(self):
        self._tokenizer.next()
        name_t = self._tokenizer.next()
        type_t = self._tokenizer.next()
        sb_t = self._tokenizer.next()
        ln_t = self._tokenizer.next()
        fac_t = self._tokenizer.next()
        off_t = self._tokenizer.next()
        sig = TelemSignalDescription(
            name=name_t.data,
            data_type=type_t.data,
            start_bit=sb_t.data,
            length=ln_t.data,
            factor=fac_t.data,
            offset=off_t.data,
        )
        nxt = self._tokenizer.peek()
        if nxt.type == TelemTokenType.TT_IDENTIFIER and nxt.data in (
            "signed",
            "unsigned",
        ):
            sig.is_signed = nxt.data == "signed"
            self._tokenizer.next()
        nxt = self._tokenizer.peek()
        if nxt.type == TelemTokenType.TT_IDENTIFIER and nxt.data in ("little", "big"):
            sig.endianness = nxt.data
            self._tokenizer.next()
        self._current_message.signals.append(sig)
        self._current_signal = sig
        self._tokenizer.reader.eatUntil("\n")
        while self._tokenizer.peek().type == TelemTokenType.TT_ENUM_PREFIX:
            self._parse_enum()

    def _parse_enum(self):
        self._tokenizer.next()
        name_t = self._tokenizer.next()
        val_t = self._tokenizer.next()
        enum = TelemEnumEntry(name=name_t.data, raw_value=val_t.data)
        self._current_signal.enums.append(enum)
        self._tokenizer.reader.eatUntil("\n")


# Data parser: assign offsets and decode snapshots
@dataclass
class TelemDataParser:
    config: TelemTelemetryConfig

    def __post_init__(self):
        # assign buffer offsets (64 bits per message)
        offset_bits = 0
        for board in self.config.boards:
            for msg in board.messages:
                msg.buffer_offset = offset_bits
                offset_bits += 64
        self.total_bits = offset_bits

    def parse_snapshot(self, buffer) -> Dict[str, float]:
        """
        Given a TelemBitBuffer 'buffer', returns mapping from "Board.Message.Signal" to physical value.
        """
        results: Dict[str, float] = {}
        for board in self.config.boards:
            for msg in board.messages:
                for sig in msg.signals:
                    bit_off = msg.buffer_offset + sig.start_bit
                    handle = TelemBitBufferHandle(offset=bit_off, size=sig.length)
                    raw_bytes = buffer.read(handle)
                    if raw_bytes is None:
                        continue
                    signed = (
                        sig.is_signed
                        if sig.is_signed is not None
                        else sig.data_type.startswith("int")
                    )
                    byteorder = sig.endianness or "little"
                    raw_val = int.from_bytes(
                        raw_bytes, byteorder=byteorder, signed=signed
                    )
                    phys = raw_val * sig.factor + sig.offset
                    key = f"{board.name}.{msg.name}.{sig.name}"
                    results[key] = phys
        return results
