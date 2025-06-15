from __future__ import annotations
import struct
import numpy as np
import yaml
from pprint import pprint
import jinja2
import builtins

from analysis.common.parser_registry import ParserVersion, parser_class, BaseParser

import struct
from typing import List, Dict

from analysis.common.parser_registry import ParserVersion, parser_class, BaseParser
from analysis.common.car_db        import CarDB

from analysis.common.parsers.telem.telem import (
    TelemTokenReader,
    TelemTokenizer,
    TelemBuilder,
    TelemTelemetryConfig,
    TelemBitBuffer,
    TelemBitBufferHandle,
    TelemDataParser,
)


class DataMapper:
    def map_snapshots(self, snapshots: List[Dict[str, str]], db: CarDB) -> CarDB:
        pass


# Assuming DataMapper and CarDB are defined elsewhere in your codebase
class YamlDataMapper(DataMapper):
    """
    Maps generic telemetry snapshots (dicts) to CarDB records based on an external mapping file.
    Mapping file format (YAML + Jinja2 templating):
    source_key: target_path
    where target_path is a dotted path into CarDB attributes, with optional [i] for array indices.
    Use '???' to indicate unmapped fields (skipped).
    Supports Jinja2 loops (including enumerate, range) in the mapping file.
    """
    def __init__(self, mapping_filename: str):
        # Load and render Jinja2 template
        print(f"Loading mapping file: {mapping_filename}")
        with open(mapping_filename, 'r') as mf:
            content = mf.read()

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('.'),
            undefined=jinja2.StrictUndefined,
            keep_trailing_newline=True
        )
        # Expose built-ins for templating
        for fn in ('enumerate', 'range', 'zip', 'len', 'int', 'float', 'bool'):
            env.globals[fn] = getattr(builtins, fn)

        template = env.from_string(content)
        rendered = template.render()
        # Parse final YAML mapping (flat dict: src_key -> dest_path)
        self.mapping: Dict[str, str] = yaml.safe_load(rendered)

        # pprint("Loaded mapping:")
        # pprint(self.mapping)

    def _set_value(self, row: np.ndarray, path: str, value: str):
        """
        Set a value in the CarDB row based on a dotted path.
        The path can include array indices (e.g., 'board.message.signal[0]').
        """
        parts = path.split('.')
        # split any that are array indices into numbers
        for i, part in enumerate(parts):
            if '[' in part and ']' in part:
                # split on the brackets
                base, index = part.split('[')
                index = int(index[:-1])

                parts[i] = (base, index)
            else:
                parts[i] = (part, None)

        pprint(parts)

        # Traverse the row to set the value
        current = row
        for i, (part, index) in enumerate(parts):
            if i == len(parts) - 1:
                # Last part, set the value
                if index is not None:
                    # If it's an indexed part, set the value at that index
                    current[index] = value
                else:
                    # Otherwise, set the value directly
                    current[part] = value
            else:
                # Not the last part, traverse deeper
                if index is not None:
                    # If it's an indexed part, get the array at that index
                    current = current[part][index]
                else:
                    # Otherwise, just get the next level
                    current = current[part]

        


    def map_snapshots(self, snapshots: List[Dict[str, str]], db: CarDB) -> CarDB:
        """
        For each generic snapshot (dict of source_key->string_value), write values into the
        underlying numpy CarDB buffer according to self.mapping.
        """
        print("Mapping telemetry snapshots to CarDB.")
        for idx, snap in enumerate(snapshots):
            row = db._db[idx]

            for src_key, value in snap.items():

                parts = src_key.split('.')
                if len(parts) < 3:
                    # if this is a single part key, then just use that to set the value in the cardb row
                    self._set_value(row, src_key, value)
                    continue

                # Construct target path from mapping
                # check if the index [board][message][signal] exists in the mapping
                board, message, signal = parts[0], parts[1], parts[2]
                board_mapping = self.mapping.get(board, {})
                message_mapping = board_mapping.get(message, {})
                signal_mapping = message_mapping.get(signal, None)
                if signal_mapping is None:
                    # If no mapping exists, skip this signal
                    print(f"Skipping unmapped signal: {src_key}")
                    continue

                if signal_mapping == '???':
                    # If the mapping is '???', skip this signal
                    print(f"Skipping signal with '???' mapping: {src_key}")
                    continue

                print(f"Mapping {src_key} to {signal_mapping} with value {value}")
        
                # now use the signal_mapping to use that attribute in the CarDB
                self._set_value(row, signal_mapping, value)




class TelemDAQParserBase(BaseParser):
    def get_mapper(self) -> DataMapper:
        pass


    def _parse_log(self, log_filename: str) -> List[Dict[str, str]]:
        """
        Parse a binary log produced by SDLogger, extracting the embedded telemetry
        config between the first board ('>') line and the last signal ('>>>') line,
        then decode all CAN snapshots into structured records.

        Returns a list of dicts mapping:
        - 'time_since_startup'
        - 'unix_time'
        - '<Board>.<Message>.<Signal>'
        to string values.
        """
        # Read all bytes
        raw = open(log_filename, "rb").read()

        # Find embedded config boundaries
        start = None
        end = None
        import io

        stream = io.BytesIO(raw)
        while True:
            pos = stream.tell()
            line = stream.readline()
            if not line:
                break
            try:
                text = line.decode("utf-8")
            except UnicodeDecodeError:
                # reached binary region
                break
            stripped = text.lstrip()
            if start is None and (stripped.startswith(">") or stripped.startswith("!!")):
                start = pos
            if start is not None and stripped.startswith(">>>"):
                end = stream.tell()
        if start is None or end is None:
            raise ValueError("Failed to locate telemetry config in log file")

        # Extract and decode config
        cfg_bytes = raw[start:end]
        cfg_text = cfg_bytes.decode("utf-8")

        # Build telemetry schema
        rdr = TelemTokenReader(cfg_text)
        tok = TelemTokenizer(rdr)
        config = TelemBuilder(tok).build()

        # Prepare data parser
        parser = TelemDataParser(config)
        rec_bytes = (parser.total_bits + 7) // 8
        record_len = 4 + 4 + rec_bytes  # uptime + unix + snapshot

        print(f"Snapshot length: {record_len} (time : {8}, frame {rec_bytes})")

        records: List[Dict[str, str]] = []
        data_region = raw[end:]
        count = len(data_region) // record_len
        for i in range(count):
            off = i * record_len
            block = data_region[off : off + record_len]
            time_since = struct.unpack_from("<I", block, 0)[0]
            unix_time = struct.unpack_from("<I", block, 4)[0]
            buf_bytes = block[8 : 8 + rec_bytes]

            bitbuf = TelemBitBuffer(bit_size=parser.total_bits, buffer=bytearray(buf_bytes))
            vals = parser.parse_snapshot(bitbuf)

            rec = {"time.time_since_startup": str(time_since), "time.unix_time": str(unix_time)}
            rec.update({k: str(v) for k, v in vals.items()})
            records.append(rec)

        return records
    
    def parse(self, filename: str) -> CarDB:
        mapper = self.get_mapper()
        snapshots = self._parse_log(filename)
        db = CarDB(len(snapshots))
        return mapper.map_snapshots(snapshots, db)