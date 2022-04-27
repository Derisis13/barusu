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

import datetime
import distutils.spawn
import getopt
import os
import subprocess
import sys
from typing import TextIO


def run_daily():
    try:
        f = open('.backupdone', "r+")
    except FileNotFoundError:
        f = open('.backupdone', "w+")
    olddate = f.read(10)
    if (olddate == str(datetime.datetime.now().date())) and (len(olddate) > 0):
        exit()
    f.seek(0, 0)
    f.write(str(datetime.datetime.now().date()))
    f.close()


def list_apt_packages():
    f = open("packages.txt", "w")
    subprocess.run(args=["dpkg", "--get-selections"], stdout=f)
    f.close()


def list_flatpak_apps():
    f = open("flatpaks.txt", "w")
    subprocess.run(args=["flatpak", "list", "--app", "--columns=origin,ref"], stdout=f)  # This will store a junk line
    f.close()


def save_dconf_settings():
    f = open("dconf_out.txt", "w")
    subprocess.run(args=["dconf", "dump", "/"], stdout=f)
    f.close()


def restore_apt_packages():
    if os.getuid() == 0:
        try:
            packagelist = open("packages.txt", "r")
        except FileNotFoundError:
            print("No packages.txt in your backup directory! Did you specify the right directory? Please check for "
                  "correct order of arguments: first -d/--backup-dir then -r/--restore!")
            exit(2)
        else:
            try:
                f = open(".backupdone", "r")
                date = f.read(10)
                f.close()
            except FileNotFoundError:
                date = "Unknown"
            print("Restoring programs and settings from ", date)
            subprocess.run(["dpkg", "--set-selections"], stdin=packagelist)
            subprocess.run(["apt-get", "dselect-upgrade"])
            print("Restoration of packages complete")
    else:
        print("You're not root! You can't restore apt packages unless you are root!")


def restore_flatpak_apps():
    try:
        f = open("flatpaks.txt", "r")
    except FileNotFoundError:
        print("No flatpaks.txt in your backup directory! Did you specify the right directory? Please check for "
              "correct order of arguments: first -d/--backup-dir then -r/--restore!")
        exit(2)
    else:
        try:
            f = open(".backupdone", "r")
            date = f.read(10)
            f.close()
        except FileNotFoundError:
            date = "Unknown"
        print("Restoring flatpaks and from ", date, "...")
        app = f.readline()
        while app:
            app = f.readline()
            subprocess.run(args=["flatpak", "install", "--user", "--assumeyes", "app"])
        print("Done!")


def restore_dconf_settings():
    try:
        config = open("dconf_out.txt", "r")
    except FileNotFoundError:
        print("No dconf_out.txt in your backup directory! Did you specify the right directory? Please check for "
              "correct order of arguments: first -d/--backup-dir then -r/--restore!")
    else:
        subprocess.run(['dconf', 'load', '/'], stdin=config)
        config.close()
        print("Restoration of settings is complete")


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
    print("Exitting...")
    exit()


def check_progs(prog):
    if prog is False:
        return False
    if distutils.spawn.find_executable(prog) is False:
        print("Missing program:" + prog + "! It is removed from the list of actions to perform...")
        return False
    return True


if __name__ == '__main__':
    backupdir = os.path.expanduser("~/.backup")
    package_manager = "apt-get"
    settings_editor = "dconf"
    restore_mode = False
    try:
        options, values = getopt.getopt(sys.argv[1:], "hd:ra:", ["help", "backup-dir=", "restore", "action="])
    except getopt.GetoptError as err:
        print("Error: ", err.msg)
        exit(1)
    else:
        for option, value in options:
            if option in ("-h", "--help"):
                print("usage: barusu [opts]\n"
                      "Options:\n"
                      "\t-h --help: show this\n"
                      "\t-d --backup-dir [directory]: set the directory for the backup/restoration "
                      "(default is ~/.backups)\n"
                      "\t-r --restore: run the restoration (from backupdir)\n"
                      "\t-a --action [a/d]: select actions to perform (default is all). Valid actions: "
                      "a - back up apt packages, d - back up dconf settings")
                exit()
            elif option in ("-d", "--backup-dir"):
                backupdir = os.path.expanduser(value)
            elif option in ("-a", "--action"):
                package_manager = False
                settings_editor = False
                if value.__contains__('a'):
                    package_manager = "apt-get"
                if value.__contains__('d'):
                    settings_editor = "dconf"
            elif option in ("-r", "--restore"):
                restore_mode = True

    actions = [package_manager, settings_editor]
    for i in actions:
        if check_progs(i) is False:
            actions.pop(actions.index(i))

    try:
        os.chdir(backupdir)
    except FileNotFoundError:
        subprocess.call(["mkdir", backupdir])
        os.chdir(backupdir)
    if restore_mode:
        restore()
        exit(0)
    run_daily()
    if actions.__contains__("apt-get"):
        list_apt_packages()
    if actions.__contains__("dconf"):
        save_dconf_settings()
