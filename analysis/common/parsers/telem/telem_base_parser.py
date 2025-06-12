from __future__ import annotations
import struct
import numpy as np

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


import yaml

class DataMapper:
    def map_snapshots(self, snapshots: List[Dict[str, str]], db: CarDB) -> CarDB:
        pass


class YamlDataMapper(DataMapper):
    """
    Maps generic telemetry snapshots (dicts) to CarDB records based on an external mapping file.
    Mapping file format (YAML):
      source_key: target_path
    where target_path is a dotted path into CarDB attributes, with optional [i] for array indices.
    """
    def __init__(self, mapping_filename: str):
        with open(mapping_filename, 'r') as mf:
            self.mapping = yaml.safe_load(mf)

    def map_snapshots(self, snapshots: List[Dict[str, str]], db: CarDB) -> CarDB:
        for idx, snap in enumerate(snapshots):
            row = db._db[idx]
            for src, dst in self.mapping.items():
                if src not in snap:
                    continue
                val = snap[src]
                # parse dst path, e.g. 'bms.cell_temps[3]'
                parts = dst.split('.')
                obj = row
                for part in parts[:-1]:
                    if '[' in part:
                        name, idx_str = part.rstrip(']').split('[')
                        obj = getattr(obj, name)[int(idx_str)]
                    else:
                        obj = getattr(obj, part)
                last = parts[-1]
                if '[' in last:
                    name, idx_str = last.rstrip(']').split('[')
                    arr = getattr(obj, name)
                    arr[int(idx_str)] = float(val)
                else:
                    # scalar assignment, convert to float if possible
                    try:
                        v = float(val)
                    except ValueError:
                        v = val
                    setattr(obj, last, v)
        return db



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

        print(cfg_text)

        # Build telemetry schema
        rdr = TelemTokenReader(cfg_text)
        tok = TelemTokenizer(rdr)
        config = TelemBuilder(tok).build()

        # Prepare data parser
        parser = TelemDataParser(config)
        rec_bytes = (parser.total_bits + 7) // 8
        record_len = 4 + 4 + rec_bytes  # uptime + unix + snapshot

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

            rec = {"time_since_startup": str(time_since), "unix_time": str(unix_time)}
            rec.update({k: str(v) for k, v in vals.items()})
            records.append(rec)

        return records
    
    def parse(self, filename: str) -> CarDB:
        mapper = self.get_mapper()
        snapshots = self._parse_log(filename)
        db = CarDB(len(snapshots))
        return mapper.map_snapshots(snapshots, db)