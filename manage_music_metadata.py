
from sys import argv
from os.path import join, isdir, isfile
from os import path, listdir
import argparse


FILE_EXT = ["m4a", "flac"]
PATH = ""
RUN = False


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


def parse():
    global PATH
    global RUN
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    PATH = args.path
    RUN = args.run

if __name__ == "__main__":
    parse()
    
    
