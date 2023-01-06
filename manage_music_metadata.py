
from sys import argv
from os.path import join, isdir, isfile, basename
from os import path, listdir

FILE_EXT = ["m4a", "flac"]


def find_files(root: str) -> list[str]:
    files = []
    for entry_name in listdir(root):
        entry_path = join(root, entry_name)
        extension = path.splitext(entry_name)[1].strip('.')
        if isfile(entry_path) and extension.lower() in FILE_EXT:
            files.append(entry_path)
        elif isdir(entry_path):
            files.extend(find_files(entry_path))
    return files


print(find_files("/Users/leana/test/"))
