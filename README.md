# FoldSync
Program that synchronizes two folders

## Task

Please implement a program that synchronizes two folders: source and replica. The program should maintain a full, identical copy of source folder at replica folder. Solve the test task by writing a program in one of these programming languages:

- Python
- C/C++
- C#

>Synchronization must be one-way: after the synchronization content of the
replica folder should be modified to exactly match content of the source
folder;

>Synchronization should be performed periodically.

>File creation/copying/removal operations should be logged to a file and to the console output;

>Folder paths, synchronization interval and log file path should be provided using the command line arguments;

>It is undesirable to use third-party libraries that implement folder synchronization;

>It is allowed (and recommended) to use external libraries implementing other well-known algorithms. For example, there is no point in implementing yet another function that calculates MD5 if you need it for the task – it is perfectly acceptable to use a  third-party (or built-in) library.


## Setup for posix systems

Download the main.py file

This program uses python dependencies click and crontab.

The scheduling of this program is handled by cron.

To install these packages run:

`pip install click`

`pip install python-crontab`

On posix system the interval is inputted in a cron syntax
[cron syntax](https://crontab.guru/)

## Setup for windows

Download the main.py file

To run on windows this program expects that python interpreter is in the windows PATH variable

This program uses python dependencies click and crontab.

The scheduling of this program is handled by cron and windows task scheduler.

`pip install click`

`pip install python-crontab`

On nt system the interval is inputted in windows task scheduler syntax
MINUTE - Specifies the number of minutes before the task should run.
HOURLY - Specifies the number of hours before the task should run.
DAILY - Specifies the number of days before the task should run.
WEEKLY Specifies the number of weeks before the task should run.
MONTHLY - Specifies the number of months before the task should run.
ONCE - Specifies that that task runs once at a specified date and time.
ONSTART - Specifies that the task runs every time the system starts. You can specify a start date, or run the task the next time the system starts.
ONLOGON - Specifies that the task runs whenever a user (any user) logs on. You can specify a date, or run the task the next time the user logs on.
ONIDLE - Specifies that the task runs whenever the system is idle for a specified period of time. You can specify a date, or run the task the next time the system is idle.

[more on the syntax](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create?source=recommendations#parameters)


## Usage on posix

`python main.py path/to/source/folder path/to/replica/folder -l path/to/log/file -r "0 0 * * *"`

## Usage on windows
`python main.py path\to\source\folder path\to\replica\folder -l path\to\log\file -r "HOURLY" -rl 5`

