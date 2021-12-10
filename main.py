import datetime
import distutils.spawn
import getopt
import os
import subprocess
import sys


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


def list_pkgs():
    f = open("packages.txt", "w")
    subprocess.run(args=["dpkg", "--get-selections"], stdout=f)
    f.close()


def save_settings():
    f = open("dconf_out.txt", "w")
    subprocess.run(args=["dconf", "dump", "/"], stdout=f)
    f.close()


def restore():
    global packagelist, config
    if os.getuid() == 0:
        try:
            os.chdir(backupdir)
        except FileNotFoundError:
            print("Backup directory not found! Does it really exist? Please check for correct order of arguments: "
                  "-d/--backup-dir -r/--restore!")
            exit(2)
        try:
            packagelist = open("packages.txt", "r")
        except FileNotFoundError:
            print("No packages.txt in your backup directory! Did you specify the right directory? Please check for "
                  "correct order of arguments: first -d/--backup-dir then -r/--restore!")
            packagelist.close()
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
            packagelist.close()
            print("Restoration of packages complete")
    else:
        print("You're not root! You can't restore packages unless you are root!")
    try:
        config = open("dconf_out.txt", "r")
    except FileNotFoundError:
        print("No dconf_out.txt in your backup directory! Did you specify the right directory? Please check for "
              "correct order of arguments: first -d/--backup-dir then -r/--restore!")
        config.close()
    else:
        subprocess.run(['dconf', 'load'], stdin=config)
        config.close()
        print("Restoration of settings is complete")
    print("Exitting...")
    exit()


def check_progs():
    apt = distutils.spawn.find_executable("apt-get")
    dconf = distutils.spawn.find_executable("dconf")
    if apt == False:
        print("Your system is not using apt as a package manager! Barusu uses apt to back up your packages. Barusu IS "
              "NOT designed to work with other packaging tools.")
    if dconf = False:
        print("Your system is not using dconf! Barusu uses dconf to back up your settings. Barusu IS "
              "NOT designed to work with other settings manager.")
    return apt, dconf


if __name__ == '__main__':
    backupdir = os.path.expanduser("~/.backup")
    try:
        options, values = getopt.getopt(sys.argv[1:], "hd:r", ["help", "backup-dir=", "restore"])
    except getopt.GetoptError as err:
        print("Error: ", err.msg)
        exit(1)
    for option, value in options:
        if option in ("-h", "help"):
            print("usage: backup_assistant [opts]\n\
                Options:\n\
                \t-h --help: show this\n\
                \t-d --backup-dir [directory]: set the directory for the backup/restoration (default is ~/.backups)\n\
                \t-r --restore: run the restoration (from backupdir)\n")
            exit()
        elif option in ("-d", "backup-dir"):
            backupdir = os.path.expanduser(value)
        elif option in ("-r", "restore"):
            restore()
            exit()

    apt, dconf = check_progs()
    if apt and dconf:
        print("System incompatibilities, exitting...")
        exit(3)

    try:
        os.chdir(backupdir)
    except FileNotFoundError:
        subprocess.call(["mkdir", backupdir])
        os.chdir(backupdir)

    run_daily()
    list_pkgs()
    save_settings()

