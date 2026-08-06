# Stage 7 — CUTS: manually pick the final videos and their order; copy them renamed cut1, cut2, ...
import sys
import shutil
from pathlib import Path


def make_cuts(video_folder):
    folder = Path(video_folder)
    videos = [f for f in folder.iterdir() if f.suffix.lower() in (".mp4", ".mov")]

    # 1. show the candidate videos, numbered
    for i, v in enumerate(videos, start=1):
        print(f"  {i}. {v.name}")

    # 2. ask for the finals IN EDIT ORDER
    answer = input("Enter finals in edit order (e.g. 3,1,5): ")
    order = [int(n) for n in answer.split(",")]      # "3,1,5" -> [3, 1, 5]

    # 3. make the cuts/ folder
    cuts_dir = folder / "cuts"
    cuts_dir.mkdir(exist_ok=True)

    # 4. copy each chosen video, renamed cut1, cut2, ... in the given order
    for position, num in enumerate(order, start=1):
        source = videos[num - 1]                   
        dest = cuts_dir / f"cut{position}{source.suffix}"                      # cut{position} + original extension
        shutil.copy2(source, dest)
        print(f"cut{position}  <-  {source.name}")


make_cuts(sys.argv[1])
