#!/bin/sh

find /files -type f \( -name '*.pdf' -o -name '*.epub' \) -exec echo "Found " {} \; -exec rmapi put {} \; -exec rm {} \;
