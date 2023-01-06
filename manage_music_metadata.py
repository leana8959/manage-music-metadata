from sys import argv, exit
from os.path import join, isdir, isfile
from os import path, listdir
import os
import argparse
import music_tag
import sys
import re


FILE_EXT = ["m4a", "flac"]
MODES = ["normalize-tracknumber", "rename", "normalize-year", "set-genre", "clear-comment"]

MODE = ""
QUIET = False
PATH = []
RUN = False
GENRE = ""


FILES = []
TRACKS = []


def load_files():
    global FILES
    for p in PATH:
        FILES.extend(find_files(p))


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
    global GENRE

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", action="extend", required=True, nargs="+")
    parser.add_argument("-m", "--mode", choices=MODES, required=True)
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--genre")

    args = parser.parse_args()
    PATH = args.path
    RUN = args.run
    QUIET = args.quiet
    MODE = args.mode
    GENRE = args.genre


def normalize_tracknumber():
    for track, path in TRACKS:
        filename = path.split("/")[-1]
        old_number = track.raw["tracknumber"]
        new_number = int(track["tracknumber"])

        if not QUIET:
            print(f'{filename}\n{old_number} -> {new_number}\n')
        if RUN and old_number != new_number:
            track["tracknumber"] = new_number
            track.save()


def normalize_year():
    for track, path in TRACKS:
        filename = path.split("/")[-1]
        old_year = track.raw["year"]
        new_year = re.findall(r"\d{4}", str(track["year"]))

        if not QUIET:
            print(f'{filename}\n{old_year} -> {new_year}\n')
        if RUN and old_year != new_year:
            track["year"] = new_year
            track.save()


def set_genre():
    # FIXME use library to handle empty genre
    global GENRE
    if not GENRE:
        print("You must provide genre")
        sys.exit(1)

    for track, path in TRACKS:
        if not QUIET:
            filename = path.split('/')[-1]
            old_genre = track["genre"]
            print(f"{filename}\n{old_genre} -> {GENRE}\n")
        if RUN and old_genre != GENRE:
            track["genre"] = GENRE
            track.save()


def rename():
    for track, path in TRACKS:
        root, old_name = os.path.split(path)
        _, extension = old_name.split('.')

        tracknumber = int(track["tracknumber"])
        title = track["title"]
        new_name = f"{tracknumber:02} - {title}.{extension}"

        old_path = join(root, old_name)
        new_path = join(root, new_name)

        if not QUIET:
            print(f"{old_name} ->\n{new_name}\n")

        if RUN and old_path != new_path:
            os.rename(old_path, new_path)

def clear_comment():
    for track, path in TRACKS:
        if not QUIET:
            filename = path.split('/')[-1]
            comment = track["comment"]
            print(f"{filename}\n{comment or 'Empty'} -> \"\"\n")
        if RUN and comment != "":
            track["comment"] = ""
            track.save()


if __name__ == "__main__":
    parse()
    load_files()
    load_tags()
    
    if MODE == "normalize-tracknumber":
        normalize_tracknumber()
    elif MODE == "rename":
        rename()
    elif MODE == "normalize-year":
        normalize_year()
    elif MODE == "set-genre":
        set_genre()
    elif MODE == "clear-comment":
        clear_comment()
