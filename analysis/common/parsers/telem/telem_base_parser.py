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

    def map_snapshots(self, snapshots: List[Dict[str, str]], db: CarDB) -> CarDB:
        """
        For each generic snapshot (dict of source_key->string_value), write values into the
        underlying numpy CarDB buffer according to self.mapping.
        """
        for idx, snap in enumerate(snapshots):
            row = db._db[idx]
            for src_key, dest_path in self.mapping.items():
                # skip unmapped entries
                if dest_path == '???':
                    continue
                # missing source: skip
                if src_key not in snap:
                    continue
                raw_val = snap[src_key]
                # Try to convert literal values (numbers, bools, lists)
                try:
                    val = ast.literal_eval(raw_val)
                except Exception:
                    val = raw_val
                # Navigate to parent of target attribute
                parts = dest_path.split('.')
                parent = row
                for part in parts[:-1]:
                    m = re.match(r"(\w+)(?:\[(\d+)\])?", part)
                    name = m.group(1)
                    idx_s = m.group(2)
                    # drill into struct or array
                    parent = parent[name]
                    if idx_s is not None:
                        parent = parent[int(idx_s)]
                # Assign to final field or array slot
                last = parts[-1]
                m = re.match(r"(\w+)(?:\[(\d+)\])?", last)
                name = m.group(1)
                idx_s = m.group(2)
                if idx_s is not None:
                    parent[name][int(idx_s)] = val
                else:
                    parent[name] = val
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