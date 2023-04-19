# Barusu - a python tool to back up your apt packages, flatpaks and dconf settings

## Usage:

barusu [opts]
Options:
    `-h --help`: show help and exit
    `-d --backup-dir [directory]`: set the directory for the backup/restoration (default is $XDG_DATA_HOME/barusu if $XDG_DATA_HOME is defined, else ~/.local/share/barusu)
    `-r --restore`: run the restoration (from backupdir). You must be root to restore, as you'll install packages. If you are backing up from a directory different from `~/.backup` you need to use the `-d`/`--backup-dir` option BEFORE the `-r`/`--restore`
    `-a --action [afd]`: select actions to perform (default is all). Valid actions: `a` - back up apt packages, `d` - back up dconf settings, `f7 - back up flatpak apps
## Installation

After downloading run in the directory you downloaded barusu to: `python3 setup.py install`

## Using with cron/anacron

In a terminal run: `crontab -e` (you might need to choose an editor to continue)
Once you see your crontab in your editor paste the following line at the end:
```
0 3 * * * barusu
```
This will run barusu every 3:00, but if the computer is off, your daily backup is missed.

Alternatively you can set up anacron (usually not installed by default)

## How it works:

backup:
1. It uses `dpkg` to get a list of all installed packages.
2. It dumps all settings using `dconf`
3. The result is three files in `$XDG_DATA_HOME/barusu` (unless specified otherwise): `packages.txt`, `flatpaks.txt` and `dconf_out.txt` (and a hidden `.backupdone` file for internal usage of the program)

restore:
(you must call the script as root when restoring!)
You have to specify actions similar to backuping, they get executed in the following order: apt -> dconf -> flatpak
It is possible to provide an alternative backup folder using option `-d` or `backup-dir` as with backups, but you need to specify the folder BEFORE the `-r`/`--restore` option
