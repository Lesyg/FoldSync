#!/usr/bin/python3

# Synchronization must be one-way: after the synchronization content of the
# replica folder should be modified to exactly match content of the source
# folder;

# Synchronization should be performed periodically.

# File creation/copying/removal operations should be logged to a file and to the console output;

# Folder paths, synchronization interval and log file path should be provided using the command line arguments;

# It is undesirable to use third-party libraries that implement folder synchronization;

# It is allowed (and recommended) to use external libraries implementing other well-known algorithms. For example, there is no point in implementing yet another function that calculates MD5 if you need it for the task – it is perfectly acceptable to use a  third-party (or built-in) library.


# handle cli arguments

# for each item in source folder 

import argparse
from pathlib import Path


parser = argparse.ArgumentParser(
    prog='FoldSync',
    description='FoldSync synchronizes the replica folder with source folder',
    epilog='Text at the bottom of help' # TODO improve this message
)

parser.add_argument("source_folder", help="path to the source folder")
parser.add_argument("replica_folder", help="path to the replica folder")
parser.add_argument('-r', '--repeat', help="repeat interval", required=False, type=int)
parser.add_argument('-l', '--log', help="path to log file", required=False)

args = parser.parse_args()

source_dir = Path(args.source)
replica_dir = Path(args.replica)

if not source_dir.exists() or not replica_dir.exists():
    print("The target directory doesn't exist")
    raise SystemExit(1)

print('SOURCE DIRECTORY:')
for entry in source_dir.iterdir():
    print(f'{entry.name}, {entry.stat().st_size}', end = ', ')
    

print('\nreplica DIRECTORY:')
for entry in replica_dir.iterdir():
    print(f'{entry.name}, {entry.stat().st_size}', end = ', ')