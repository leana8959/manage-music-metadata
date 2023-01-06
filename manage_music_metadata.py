from sys import argv, exit
from os.path import join, isdir, isfile
from os import path, listdir
import argparse
import music_tag


FILE_EXT = ["m4a", "flac"]
MODE = ""
QUIET = False
PATH = ""
RUN = False
FILES = []
TRACKS = []


def load_files():
    global FILES
    FILES = find_files(PATH)


def find_files(root: str) -> list[str]:
    files = []
    for entry_name in listdir(root):
        entry_path = join(root, entry_name)
        extension = entry_name.split('.')[-1]
        if isfile(entry_path) and extension.lower() in FILE_EXT:
            files.append(entry_path)
        elif isdir(entry_path):
            files.extend(find_files(entry_path))
    return files


def load_tags():
    global TRACKS
    TRACKS = [
        (music_tag.load_file(file), file)
        for file in FILES
    ]


def parse():
    global PATH
    global RUN
    global QUIET
    global MODE 

    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--mode", choices=["normalize-tracknumber"], required=True)

    args = parser.parse_args()
    PATH = args.path
    RUN = args.run
    QUIET = args.quiet
    MODE = args.mode



def normalize_tracknumber():
    for track, path in TRACKS:
        if not QUIET:
            print(f'{path.split("/")[-1]}\n{track.raw["tracknumber"]} -> {track["tracknumber"]}\n')
        track["tracknumber"] = track["tracknumber"]
        if RUN:
            track.save()



if __name__ == "__main__":
    parse()
    load_files()
    load_tags()
    if MODE == "normalize-tracknumber":
        normalize_tracknumber()
    



