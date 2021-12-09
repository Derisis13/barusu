import os
import subprocess
import datetime
import sys
import getopt


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
    # todo


if __name__ == '__main__':
    backupdir = "/home/lacko/.backup"
    try:
        options, values = getopt.getopt(sys.argv[1:], "hd:r", ["help", "backup-dir=", "restore"])
    except getopt.GetoptError as err:
        print("Error: ", err.msg)
        exit(1)
    for option, value in options:
        if option in ("h", "help"):
            print("usage: <name> [opts]\n\
                Options:\n\
                \t-h --help: show this\n\
                \t-d --backup-dir [directory]: set the directory for the backup/restoration (default is ~/.backups)\n\
                \t-r --restore: run the restoration (from backupdir)\n")  # todo: <name>
            exit()
        elif option in("d", "backup-dir"):
            backupdir = value
        elif option in("r", "restore"):
            restore()
            exit()

    try:
        # os.chdir("/run/user/1000/gvfs/smb-share:server=ds_panni.local,share=lacko/Backup/T490")
        os.chdir(backupdir)
    except FileNotFoundError:
        subprocess.call(["mkdir", backupdir])
    run_daily()
    list_pkgs()
    save_settings()
