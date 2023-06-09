#!/usr/bin/env python3
import hashlib
import logging
import os
import shutil
import string
import sys
from pathlib import Path

import click
import crontab

# Specifies how many bytes are read at once when computing SHA1 hash
SHA1_READ_BYTES = 65536


@click.command()
@click.argument('source_dir', type=click.Path(path_type=Path))
@click.argument('replica_dir', type=click.Path(path_type=Path))
@click.option('-l', '--log', type=click.Path(path_type=Path), help='Path to the log file')
@click.option('-r', '--repeat',
              help="Repeat interval in cron syntax or windows task scheduler type, when not specified program runs "
                   "only once",
              type=click.STRING)
@click.option('-rv', '--repeat-value',
              help="Repeat interval length for windows task scheduler, when not specified defaults to 1",
              type=click.INT)
def run_sync(source_dir: Path, replica_dir: Path, log: Path, repeat: string, repeat_value: int) -> None:
    """
    Synchronize replica_dir with source_dir\n
    :param source_dir: Path to the source directory\n
    :param replica_dir: Path to the destination directory
    :return None
    """
    setup_logging(log)
    logging.info("Starting application")

    logging.info("Validating directories")
    validate(source_dir, replica_dir)

    if repeat:
        setup_repeat(repeat, source_dir, replica_dir, log, repeat_value if repeat_value is not None else 1)

    logging.info("Starting synchronization")
    copy_files(source_dir, replica_dir)

    logging.info("Synchronization successful, ending program\n")


def setup_repeat(interval: string, source: Path, replica: Path, log: Path, interval_value: int) -> None:
    """
    Creates either a cron job or a windows task schedule for the user that ran this script
    :param interval: interval in which to run this script in a cron syntax or windows task syntax
    :param source: path to the source directory
    :param replica: path to the replica directory
    :param log: path to the log file
    :param interval_value: interval value for windows task schedule
    :return: None
    """
    if os.name == 'nt':
        setup_repeat_win(interval, source, replica, log, interval_value)
    else:
        setup_repeat_posix(interval, source, replica, log)


def setup_repeat_win(interval_type: string, source: Path, replica: Path, log: Path, interval_value: int) -> None:
    """
    Creates a windows task schedule for the user that ran this script
    :param interval_type: interval in which to run this script in a cron syntax or windows task syntax
    :param source: path to the source directory
    :param replica: path to the replica directory
    :param log: path to the log file
    :param interval_value: interval value for windows task schedule
    :return: None
    """
    logging.info(f"Installing script on windows to run at {interval_type} interval")

    task_name = "FOLD_SYNC_TASK"
    task_command = f"python {Path(sys.argv[0]).absolute()} {source.absolute()} {replica.absolute()} -l {log.absolute()}"

    try:
        logging.info(
            f"Creating scheduled task: schtasks /Create /TN {task_name} /TR \"{task_command}\" /SC {interval_type} /MO {str(interval_value)} /RU {os.getlogin()} /F")
        os.system(
            f"schtasks /Create /TN {task_name} /TR \"{task_command}\" /SC {interval_type} /MO {str(interval_value)} /RU {os.getlogin()} /F")
    except Exception as e:
        logging.error(f"Failed to setup scheduled task: {e}")
        logging.error("Script will not run repeatedly")
        return
    logging.info("scheduled task created successfully")


def setup_repeat_posix(interval: string, source: Path, replica: Path, log: Path) -> None:
    """
    Creates a cron job for the user that ran this script
    :param interval: interval in which to run this script in a cron syntax or windows task syntax
    :param source: path to the source directory
    :param replica: path to the replica directory
    :param log: path to the log file
    :return: None
    """
    logging.info(f"Installing script for posix system to run at {interval} interval")
    logging.info(
        f"Creating cron job: {interval} {Path(sys.argv[0]).absolute()} {source.absolute()} {replica.absolute()} -l {log.absolute()}")
    cron = crontab.CronTab(user=os.getlogin())
    jobs = cron.find_comment("FOLD_SYNC_JOB")
    for job in jobs:
        cron.remove(job)
    job = cron.new(
        command=f"{Path(sys.argv[0]).absolute()} {source.absolute()} {replica.absolute()} -l {log.absolute()}",
        comment="FOLD_SYNC_JOB")
    try:
        job.setall(interval)
    except ValueError:
        logging.error(f"This cron syntax {interval} is not valid")
        logging.error("Script will not run repeatedly")
        return

    if not job.is_valid():
        logging.error("Cron job is not valid")
        logging.error("Script will not run repeatedly")
        return
    try:
        cron.write()
    except Exception as e:
        logging.error("Something went wrong while creating cron job")
        logging.debug(e)
        return
    logging.info("Created cron job successfully")


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
            if not hash_file(file) == hash_file(destination.joinpath(file.name)):
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


def hash_file(file: Path) -> string:
    """
    Computes the hash of the file
    :param file: path to the file to has
    :return: returns the hash as a string
    """
    with open(file, 'rb') as f:
        sha1 = hashlib.sha1()
        while chunk := f.read(SHA1_READ_BYTES):
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


def setup_logging(file: Path) -> None:
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
