from sys import argv, exit
from os.path import join, isdir, isfile
from os import path, listdir
import os
import argparse
import music_tag
import sys
import re


FILE_EXT = ["m4a", "flac"]
TRASH_EXT = ["log", "m3u", "jpeg", "jpg", "png"]
MODES = ["normalize-tracknumber", "rename",
         "normalize-year", "set-genre", "clear-comment", "remove-junk", "clear-lyrics"]

MODE = ""
QUIET = False
PATH = []
RUN = False
GENRE = ""


FILES = []
TRASHES = []
TRACKS = []


def load_files():
    global FILES
    global TRASHES

    for p in PATH:
        files, trashes = find_files(p)
        FILES.extend(files)
        TRASHES.extend(trashes)


def find_files(root: str) -> list[str]:
    files = []
    trashes = []
    for entry_name in listdir(root):
        entry_path = join(root, entry_name)
        extension = entry_name.split('.')[-1]

        if isfile(entry_path) and extension.lower() in FILE_EXT:
            files.append(entry_path)
        elif isfile(entry_path) and extension.lower() in TRASH_EXT:
            trashes.append(entry_path)
        elif isdir(entry_path):
            f, t = find_files(entry_path)
            files.extend(f)
            trashes.extend(t)

    return (files, trashes)


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
        try:
            new_number = int(track["tracknumber"])
        except ValueError:
            print(f"{filename}\nCouldn't parse track number, skipping\n")
            new_number = old_number
            continue

        if not QUIET:
            print(f'{filename}\n{old_number} -> {new_number}\n')
        if RUN and old_number != new_number:
            track["tracknumber"] = new_number
            track.save()


def normalize_year():
    for track, path in TRACKS:
        filename = path.split("/")[-1]
        old_year = track.raw["year"]
        new_year = re.findall(r"\d{4}|$", str(track.raw["year"]))[0]

        if not QUIET:
            print(f'{filename}\n{old_year} -> {new_year}\n')
        if RUN and old_year != new_year:
            track.raw["year"] = new_year
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
        extension = old_name.split('.')[-1]

        try:
            tracknumber = f'{int(track["tracknumber"]):02}'
        except ValueError:
            tracknumber = track.raw["tracknumber"]
        title = track["title"]
        new_name = f"{tracknumber} - {title}.{extension}".replace('/', ' ')

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

def clear_lyrics():
    for track, path in TRACKS:
        if not QUIET:
            filename = path.split('/')[-1]
            lyrics = track["lyrics"]
            print(f"{filename}\n{lyrics or 'Empty'} -> \"\"\n")
        if RUN and lyrics != "":
            track["lyrics"] = ""
            track.save()


def remove_junk():
    for trash in TRASHES:
        if not QUIET:
            print(trash)
        if RUN:
            os.remove(trash)


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
    elif MODE == "remove-junk":
        remove_junk()
    elif MODE == "clear-lyrics":
        clear_lyrics()
