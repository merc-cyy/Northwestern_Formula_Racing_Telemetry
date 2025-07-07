#!/usr/bin/env python3
"""
cpp_struct_to_py_fmt.py

Read a C/C++ struct from an input file, and generate a Python module
that defines a struct-format string (using struct.pack/unpack syntax),
including explicit padding so that calcsize(fmt) == sizeof(C struct).

Usage:
    python cpp_struct_to_py_fmt.py in_struct.h out_fmt.py
"""

import re
import sys
import argparse
from textwrap import indent

# Map C/C++ types to (struct-module code, size, alignment)
TYPE_INFO = {
    'bool':     ('?', 1, 1),
    'int8_t':   ('b', 1, 1),
    'uint8_t':  ('B', 1, 1),
    'int16_t':  ('h', 2, 2),
    'uint16_t': ('H', 2, 2),
    'int32_t':  ('i', 4, 4),
    'uint32_t': ('I', 4, 4),
    'int64_t':  ('q', 8, 8),
    'uint64_t': ('Q', 8, 8),
    'float':    ('f', 4, 4),
    'double':   ('d', 8, 8),
}

_struct_re = re.compile(r'struct\s+(\w+)\s*\{([^}]+)\};', re.MULTILINE | re.DOTALL)
_field_re  = re.compile(r'\s*(\w+)\s+(\w+)(?:\s*\[\s*(\w+)\s*\])?(?:\s*=\s*[^;]+)?;')

def parse_struct(text):
    m = _struct_re.search(text)
    if not m:
        sys.exit("No struct found in input.")
    name = m.group(1)
    body = m.group(2)
    fields = []
    for line in body.splitlines():
        fm = _field_re.match(line)
        if not fm:
            continue
        ctype, name, arr = fm.groups()
        if ctype not in TYPE_INFO:
            sys.exit(f"Unsupported type: {ctype}")
        count = int(arr) if arr else 1
        fields.append((ctype, name, count))
    return name, fields

def build_fmt_and_size(fields):
    """Return (fmt_pieces, total_size, struct_align)."""
    offset = 0
    struct_align = 1
    fmt_pieces = []
    for ctype, name, count in fields:
        code, size, align = TYPE_INFO[ctype]
        struct_align = max(struct_align, align)
        # add padding to align this field
        pad = (align - (offset % align)) % align
        if pad:
            fmt_pieces.append((f'{pad}x', f'# pad {pad} bytes before {name}'))
            offset += pad
        # now the field
        if count == 1:
            fmt_pieces.append((code, f'# {name} : {ctype}'))
            offset += size
        else:
            fmt_pieces.append((f'{count}{code}', f'# {name}[{count}] : {ctype}'))
            offset += size * count
    # final tail padding to make struct size a multiple of struct_align
    tail = (struct_align - (offset % struct_align)) % struct_align
    if tail:
        fmt_pieces.append((f'{tail}x', f'# tail pad {tail} bytes'))
        offset += tail
    return fmt_pieces, offset, struct_align

def generate_python_module(struct_name, fmt_pieces, c_size):
    lines = []
    lines.append(f"# Auto-generated from struct {struct_name}")
    lines.append("import struct")
    lines.append("")
    lines.append(f"def validate_size():")
    lines.append(f"    c_size = {c_size}")
    lines.append(f"    py_size = struct.calcsize(fmt)")
    lines.append(f"    assert c_size == py_size, f\"Size mismatch: C={{c_size}}, Python={{py_size}}\"")
    lines.append("")
    lines.append("fmt = ''.join([")
    # prefix with little-endian '<' — adjust if needed
    lines.append("    '<',  # little-endian, standard alignment")
    for code, comment in fmt_pieces:
        lines.append(f"    '{code}', {comment}")
    lines.append("])")
    lines.append("")
    lines.append("validate_size()")
    lines.append("")
    return "\n".join(lines)

def register_subparser(subparser):
    subparser.add_argument("input", help="C/C++ file with a single struct")
    subparser.add_argument("output", help="Path to write generated Python module")

def main(args):
    text = open(args.input).read()
    struct_name, fields = parse_struct(text)
    fmt_pieces, c_size, struct_align = build_fmt_and_size(fields)
    py_module = generate_python_module(struct_name, fmt_pieces, c_size)

    with open(args.output, "w") as f:
        f.write(py_module)
    print(f"Wrote Python module with fmt for struct '{struct_name}' ({c_size} bytes) to {args.output}")

if __name__ == '__main__':
    main()
