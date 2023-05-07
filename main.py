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

import click
from pathlib import Path
import shutil
import os


# @click.option('-l', '--log', help="Path to the log file")
@click.command()
@click.argument('source_dir', type=click.Path(path_type=Path))
@click.argument('replica_dir', type=click.Path(path_type=Path))
def run_sync(source_dir: Path, replica_dir: Path) -> None:
    """
    Synchronize replica_dir with source_dir\n
    :param source_dir: Path to the source directory\n
    :param replica_dir: Path to the destination directory
    """
    if not source_dir.exists() or not replica_dir.exists():
        click.echo("The target directory doesn't exist")
        raise SystemExit(1)

    click.echo('SOURCE DIRECTORY:')

    simple_sync(source_dir, replica_dir)

    # copy_files(source_dir, replica_dir)

    print('\nREPLICA DIRECTORY:')

    for entry in replica_dir.iterdir():
        click.echo(f'{entry.name}, size: {entry.stat().st_size}')

    # parser = argparse.ArgumentParser(
    #     prog='FoldSync',
    #     description='FoldSync synchronizes the replica folder with source folder',
    #     epilog='Text at the bottom of help' # TODO improve this message
    # )

    # parser.add_argument("source_folder", help="path to the source folder")
    # parser.add_argument("replica_folder", help="path to the replica folder")
    # parser.add_argument('-r', '--repeat', help="repeat interval", required=False, type=int)
    # parser.add_argument('-l', '--log', help="path to log file", required=False)

def simple_sync(source: Path, destination: Path) -> None:
    """
    Very simple synchronization function
    First it recursively clears the folder, and then it recursively copies the folder
    :param source: Path to the source folder
    :param destination: Path to the destination folder
    :return:
    """
    shutil.rmtree(destination)
    shutil.copytree(source, destination)

def copy_files(source: Path, destination: Path) -> None:
    if not destination.exists():
        Path.mkdir(destination)
    for file in source.iterdir():
        if file.is_dir():
            copy_files(file, destination.joinpath(file.name))
        else:
            click.echo(f'Copying file {file.name} of size: {file.stat().st_size} from {source} directory to {destination} directory')
            shutil.copy2(os.path.join(source, file.name), destination)


if __name__ == '__main__':
    run_sync()
