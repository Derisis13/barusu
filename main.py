# Copyright 2021 László Párkányi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import shutil
import getopt
import os
import subprocess
import sys


def open_backup_file(filename):
    global backupfile
    try:
        backupfile = open(filename, "r")
    except FileNotFoundError:
        print("No " + filename + " in your backup directory! \n"
              "Did you specify the right directory? Please check for correct order of arguments: -d/--backup-dir"
              " -r/--restore -a/--action!")
        exit(2)
    return backupfile


def save_apt_packages():
    f = open("packages.txt", "w")
    subprocess.run(args=["dpkg", "--get-selections"], stdout=f)
    f.close()


def save_flatpak_apps():
    f = open("flatpaks.txt", "w")
    subprocess.run(args=["flatpak", "list", "--app", "--columns=ref"], stdout=f)
    f.close()


def save_dconf_settings():
    f = open("dconf_out.txt", "w")
    subprocess.run(args=["dconf", "dump", "/"], stdout=f)
    f.close()


def restore_apt_packages():
    if os.getuid() == 0:
        packagelist = open_backup_file("packages.txt")
        print("Restoring apt packages...")
        subprocess.run(["dpkg", "--set-selections"], stdin=packagelist)
        subprocess.run(["apt-get", "dselect-upgrade"])
        print("Done!")
    else:
        print("You're not root! You can't restore apt packages unless you are root!")


def restore_flatpak_apps():
    flatpaklist = open_backup_file("flatpaks.txt")
    print("Restoring flatpak applications...")
    while True:
        app = flatpaklist.readline()
        if app == "":
            break
        subprocess.run(args=["flatpak", "install", "--user", "--assumeyes", app[0:-1]])
    print("Done!")


def restore_dconf_settings():
    config = open_backup_file("dconf_out.txt")
    print("Restoring dconf settings...")
    subprocess.run(['dconf', 'load', '/'], stdin=config)
    config.close()
    print("Done!")


def restore():
    try:
        os.chdir(backupdir)
    except FileNotFoundError:
        print("Backup directory not found! Does it really exist? Please check for correct order of arguments: "
              "-d/--backup-dir -r/--restore!")
        exit(2)
    if actions.__contains__("apt-get"):
        restore_apt_packages()
    if actions.__contains__("dconf"):
        restore_dconf_settings()
    if actions.__contains__("flatpak"):
        restore_flatpak_apps()
    print("Exiting...")
    exit()


def check_progs(prog):
    if prog is False:
        return False
    if shutil.which(prog) is False:
        print("Missing program:" + prog + "! It is removed from the list of actions to perform...")
        return False
    return True


if __name__ == '__main__':
    try:
        data_dir = os.environ["XDG_DATA_HOME"]
    except KeyError as e:
        data_dir = os.path.expanduser("~/.local/share")
    backupdir = os.path.join(data_dir, "barusu/")
    package_manager = "apt-get"
    settings_editor = "dconf"
    flatpak = "flatpak"
    restore_mode = False
    try:
        options, values = getopt.getopt(sys.argv[1:], "hd:ra:", ["help", "backup-dir=", "restore", "action="])
    except getopt.GetoptError as err:
        print("Error: ", err.msg)
        exit(1)
    else:
        for option, value in options:
            if option in ("-h", "--help"):
                print("usage: " + sys.argv[0] + " [opts]\n"
                      "Options:\n"
                      "\t-h --help: show this\n"
                      "\t-d --backup-dir [directory]: set the directory for the backup/restoration "
                      "(default is $XDG_DATA_HOME/barusu if $XDG_DATA_HOME is defined, else ~/.local/share/barusu)\n"
                      "\t-r --restore: run the restoration (from backupdir)\n"
                      "\t-a --action [afd]: select actions to perform (default is all). Valid actions: "
                      "a - back up apt packages, d - back up dconf settings, f - back up flatpak apps")
                exit()
            elif option in ("-d", "--backup-dir"):
                backupdir = os.path.expanduser(value)
            elif option in ("-a", "--action"):
                package_manager = False
                settings_editor = False
                flatpak = False
                if value.__contains__('a'):
                    package_manager = "apt-get"
                if value.__contains__('d'):
                    settings_editor = "dconf"
                if value.__contains__('f'):
                    flatpak = "flatpak"
            elif option in ("-r", "--restore"):
                restore_mode = True

    actions = [package_manager, settings_editor, flatpak]
    for i in actions:
        if check_progs(i) is False:
            actions.pop(actions.index(i))

    try:
        os.chdir(backupdir)
    except FileNotFoundError:
        os.makedirs(backupdir, mode=0o774)
        os.chdir(backupdir)
    if restore_mode:
        restore()
        exit(0)
    if actions.__contains__("apt-get"):
        save_apt_packages()
    if actions.__contains__("dconf"):
        save_dconf_settings()
    if actions.__contains__("flatpak"):
        save_flatpak_apps()
