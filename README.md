# Barusu - a python tool to back up your apt packages and dconf settings

## Usage:

backup_assistant [opts]
Options:
    `-h --help`: show help and exit
    `-d --backup-dir [directory]`: set the directory for the backup/restoration (default is ~/.backups)
    `-r --restore`: run the restoration (from backupdir). You must be root to restore, as you'll install packages. If you are backing up from a directory different from `~/.backup` you need to use the `-d`/`--backup-dir` option BEFORE the `-r`/`--restore`

## Installation

After downloading run in the directory you downloaded barusu to: `python3 setup.py install`

## Using with cron

In a terminal run: `crontab` (you might need to choose an editor to continue)
Once you see your crontab in your editor paste the following line at the end:
`0 * * * * barusu`
This will attempt to run barusu hourly, however it'll only fully run once daily and exit every other time to save system resources.

## How it works:

backup:
1. It uses `dpkg` to get a list of all installed packages.
2. It dumps all settings using `dconf`
3. The result is two files in `~/.backup` (unless specified otherwise): `packagelist.txt` and `dconf_out.txt` (and a hidden `.backupdone` file for internal usage of the program

restore:
(you must call the script as root when restoring!)
1. It uses `dpkg` to set a list of operations exported in `~/.backup/packagelist.txt` then calls `apt-get` to install them
2. It uses `dconf` to load settings exported in `~/.backup/dconf_out.txt`
It is possible to provide an alternative backup folder using option `-d` or `backup-dir` as with backups, but you need to specify the folder BEFORE the `-r`/`--restore` option
