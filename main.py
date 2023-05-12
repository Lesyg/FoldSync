#!/usr/bin/python3
import string

# Synchronization must be one-way: after the synchronization content of the
# replica folder should be modified to exactly match content of the source
# folder;

# Synchronization should be performed periodically.

# Folder paths, synchronization interval and log file path should be provided using the command line arguments;


import click
from pathlib import Path
import shutil
import os
import logging
import hashlib


# parser.add_argument('-r', '--repeat', help="repeat interval", required=False, type=int)

@click.command()
@click.argument('source_dir', type=click.Path(path_type=Path))
@click.argument('replica_dir', type=click.Path(path_type=Path))
@click.option('-l', '--log', type=click.Path(path_type=Path), help='Path to the log file')
def run_sync(source_dir: Path, replica_dir: Path, log: Path) -> None:
    """
    Synchronize replica_dir with source_dir\n
    :param source_dir: Path to the source directory\n
    :param replica_dir: Path to the destination directory
    :param log: Path to the log file
    :return None
    """

    setup_log(log)

    logging.info(f"Starting synchronization program")

    logging.info("Validating directories")
    validate(source_dir, replica_dir)

    logging.info("Starting synchronization")
    copy_files(source_dir, replica_dir)

    logging.info("Synchronization successful, ending program\n")


def copy_files(source: Path, destination: Path) -> None:
    """
    Copies all files from source directory to target directory
    :param source: source directory
    :param destination: destination directory
    :return: None
    """
    if not destination.exists():
        Path.mkdir(destination)

    remove_unwanted(source, destination)

    for file in source.iterdir():
        if file.is_dir():
            copy_files(file, destination.joinpath(file.name))
        else:
            if not destination.joinpath(file.name).exists():
                copy_file(source, destination, file)
                continue
            if file.stat().st_size != destination.joinpath(file.name).stat().st_size:
                copy_file(source, destination, file)
                continue
            if not sha_eq(file, destination.joinpath(file.name)):
                copy_file(source, destination, file)


def copy_file(source: Path, destination: Path, file: Path) -> None:
    """
    Copy a file from source directory to destination directory
    :param source: source directory
    :param destination: destination directory
    :param file: file to copy
    :return: None
    """
    logging.info(
        f'Copying file {file.name} of size: {file.stat().st_size} from {source.absolute()} directory to {destination.absolute()} directory')
    shutil.copy2(os.path.join(source, file.name), destination)


def sha_eq(source: Path, destination: Path) -> bool:
    """
    Computes and compares 2 hashes
    :param source: path to the first file
    :param destination: path to the second file
    :return: true when hashes are equal, false when they differ
    """
    return hash_file(source) == hash_file(destination)


def hash_file(file: Path) -> string:
    """
    Computes the hash of the file
    :param file: path to the file to has
    :return: returns the hash as a string
    """
    with open(file, 'rb') as f:
        sha1 = hashlib.sha1()
        while chunk := f.read(65536):
            sha1.update(chunk)

    return sha1.hexdigest()


def remove_unwanted(source: Path, destination: Path) -> None:
    """
    Removes files and directories from target directory
    that are not present in the source directory
    :param source: path to source directory
    :param destination: path to target directory
    :return: None
    """
    path_set = set()
    for file in destination.iterdir():
        path_set.add(file)

    for file in source.iterdir():
        if destination.joinpath(file.name) in path_set:
            path_set.remove(destination.joinpath(file.name))

    for file in path_set:
        if file.is_dir():
            remove_directory(file)
        else:
            logging.info(f"Removing unwanted file {file.absolute()} from destination directory")
            file.unlink()


def remove_directory(file: Path) -> None:
    if file.is_dir():
        remove_directory(file)
    else:
        logging.info(f"Removing unwanted file {file.absolute()} from destination directory")
        file.unlink()


def validate(source_dir: Path, replica_dir: Path) -> None:
    """
    Validates the source and target directory
    If the target directory doesn't exist it creates it
    :param source_dir:
    :param replica_dir:
    :return: None
    """
    if not os.access(source_dir, os.R_OK):
        logging.error(f"The source directory {source_dir} is not accessible")
        logging.error("Exiting application\n")
        raise SystemExit(1)

    if not source_dir.exists():
        logging.error(f"The source directory {source_dir.absolute()} doesn't exist")
        logging.error("Can't perform synchronization")
        logging.error("Exiting application\n")
        raise SystemExit(1)

    if not replica_dir.exists():
        logging.warning(f"The target directory {replica_dir.absolute()} doesn't exist")
        logging.info(f"Creating target directory {replica_dir.absolute()}")
        Path.mkdir(replica_dir)


def setup_log(file: Path) -> None:
    """
    Configures logging
    :param file: path to the file logs will be written to
    :return: None
    """
    if file:
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO, handlers=[
            logging.FileHandler(file),
            logging.StreamHandler()
        ])
    else:
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG, handlers=[
            logging.StreamHandler()
        ])


if __name__ == '__main__':
    run_sync()
