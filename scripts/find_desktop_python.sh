#!/bin/bash
# Find a Python on Mac that can run the tkinter desktop helper.
# Prints the full path to stdout; exit 1 if none found.
set -u

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

for candidate in \
  /opt/homebrew/bin/pythonw \
  /opt/homebrew/bin/python3 \
  /usr/local/bin/pythonw \
  /usr/local/bin/python3 \
  /usr/bin/pythonw \
  /Library/Frameworks/Python.framework/Versions/3.12/bin/pythonw \
  /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
  pythonw3 pythonw python3
do
  if [[ -x "$candidate" ]] || command -v "$candidate" >/dev/null 2>&1; then
    cmd="$candidate"
    [[ -x "$candidate" ]] || cmd="$(command -v "$candidate")"
    if "$cmd" -c "import tkinter" 2>/dev/null; then
      echo "$cmd"
      exit 0
    fi
  fi
done

exit 1
