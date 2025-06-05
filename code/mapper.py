#!/usr/bin/env python
import sys
import csv

reader = csv.reader(sys.stdin)
header = next(reader)  # skip header

for row in reader:
    # merged.csv has identical columns to USvideos.csv
    video_id = row[0]
    trending_date = row[1]
    print(f"{video_id}\t{trending_date}")