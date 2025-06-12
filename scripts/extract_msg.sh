#!/usr/bin/env bash
# extract_full_names.sh — prints Board.Message.Signal for each signal in a telem file
# Usage: ./extract_full_names.sh telemetry_config.txt

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <telem_file>"
  exit 1
fi

current_board=""
current_msg=""

while IFS= read -r line; do
  # Board lines: start with a single '>'
  if [[ $line =~ ^\>\ ([^[:space:]]+) ]]; then
    current_board="${BASH_REMATCH[1]}"
    current_msg=""
    continue
  fi

  # Message lines: start with '>>'
  if [[ $line =~ ^\>\>\ ([^[:space:]]+) ]]; then
    current_msg="${BASH_REMATCH[1]}"
    continue
  fi

  # Signal lines: start with '>>>'
  if [[ $line =~ ^\>\>\>\ ([^[:space:]]+) ]]; then
    signal="${BASH_REMATCH[1]}"
    # Only print if we have both board and message context
    if [[ -n $current_board && -n $current_msg ]]; then
      echo "${current_board}.${current_msg}.${signal}"
    fi
  fi
done < "$1"
