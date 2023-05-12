#!/usr/bin/python3

# Synchronization must be one-way: after the synchronization content of the
# replica folder should be modified to exactly match content of the source
# folder;

# Synchronization should be performed periodically.

# File creation/copying/removal operations should be logged to a file and to the console output;

# Folder paths, synchronization interval and log file path should be provided using the command line arguments;

# It is undesirable to use third-party libraries that implement folder synchronization;

# It is allowed (and recommended) to use external libraries implementing other well-known algorithms. For example, there is no point in implementing yet another function that calculates MD5 if you need it for the task – it is perfectly acceptable to use a  third-party (or built-in) library.



import click
from pathlib import Path
import shutil
import os
import logging


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
    """

    setup_log(log)

    logging.info(f"Starting synchronization program")

    logging.info("Validating directories")
    validate(source_dir, replica_dir)

    logging.info("Starting synchronization")

    copy_files(source_dir, replica_dir)

    logging.info("Synchronization succesfull, ending program\n")


def copy_files(source: Path, destination: Path) -> None:
    if not destination.exists():
        Path.mkdir(destination)
    for file in source.iterdir():
        if file.is_dir():
            copy_files(file, destination.joinpath(file.name))
        else:
            logging.info(
                f'Copying file {file.name} of size: {file.stat().st_size} from {source.absolute()} directory to {destination.absolute()} directory')
            shutil.copy2(os.path.join(source, file.name), destination)


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
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO, handlers=[
            logging.StreamHandler()
        ])


if __name__ == '__main__':
    run_sync()
