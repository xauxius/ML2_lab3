# various utilities for matchmaking

import glob
import os
import zipfile
import shutil


def uncompressed_underlimit(zipfile):
    total_size = 0
    total_count = 0
    for z in zipfile.filelist:
        total_count = 0
        if (z.is_dir()):
            continue
        with zipfile.open(z) as f:
            while (l := f.read(DATA_LIMIT)):
                total_size = total_size + len(l)
                if (total_size > DATA_LIMIT):
                    return False

    if total_count > 2000:  # too much files
        return False
    return True
    pass


def search_entrypoint(zipfile):
    """ return True, entrypoint or False, message"""
    lst = zipfile.filelist
    first_dir_files = list(filter(lambda x: x.filename.count("/") == 1 and x.is_dir() == False, lst))
    root_dir_files = list(filter(lambda x: x.filename.count("/") == 0 and x.is_dir() == False, lst))

    to_consider = root_dir_files

    if len(root_dir_files) == 0:
        to_consider = first_dir_files

    to_consider = list(filter(lambda x: x.filename.split("/")[-1] not in IGNORE_FILES, to_consider))

    if len(to_consider) == 0:
        return False, "no entry point found"

    if len(to_consider) == 1:
        return True, to_consider[0].filename

    if len(to_consider) > 1:
        for j in to_consider:
            if j.filename.endswith("main.py"):
                return True, j.filename
        return False, "no main.py found"


def collect_players(workdir="testai"):
    """ return tuple with with zip archives and main py files
    """

    players = []

    g = glob.glob(f"{workdir}/*.zip")
    for i in g:
        if os.stat(i).st_size > DATA_LIMIT:
            print(f"ignoring `{i}' because too big, submitted size is {DATA_LIMIT/1024/1024:.2f} Mb")
            continue
        with zipfile.ZipFile(i) as z:
            if not uncompressed_underlimit(z):
                print(f"ignoring `{i}' because uncompressed data too big")
                continue

            found, ep_name_error = search_entrypoint(z)
            if not found:
                print(f"ignoring `{i}' due entry point failure: {ep_name_error}")
                continue

        players.append((i, ep_name_error, os.path.basename(i)))

    return players


def extract_data(players, workdir="tmp"):
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.mkdir(workdir)

    for i in players:
        with zipfile.ZipFile(i[0]) as z:
            bn = os.path.basename(i[0])
            z.extractall(f"{workdir}/{bn}")
