#!/usr/bin/env python
import sys

current_video = None
dates = set()

for line in sys.stdin:
    parts = line.strip().split('\t')
    if len(parts) != 2:
        continue
    video_id, date = parts

    if current_video and video_id != current_video:
        print(f"{current_video}\t{len(dates)}")
        dates.clear()

    current_video = video_id
    dates.add(date)

# final video
if current_video:
    print(f"{current_video}\t{len(dates)}")