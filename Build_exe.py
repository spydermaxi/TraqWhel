#!/usr/bin/env python3
#--------------------------------------------------------------------#
#                                                                    #
#                        Python script                               #
#                                                                    #
#--------------------------------------------------------------------#
#
# Ident        : Build_exe.py
__version__ = "1.0.0"
__author__ = "Adrian Loo"
"""
Build_exe.py is built for easy CI of the target app
"""
#
# History:
# 2021-10-20: 1.0.0 [Adrian Loo] first commit
# 2021-10-25: 1.0.0 [Adrian Loo] create clear_scraps(), make_app_exe(), make_install_exe(). Fix syntax error. execute sys.exit() on end
# 2021-10-25: 1.0.0 [Adrian Loo] Add iexpress automation using SED file is SED file exists
#
#--------------------------------------------------------------------#
#                                                                    #
#                       BSD 3-Clause License                         #
#              Copyright (c) 2021, AXONBOTS PTE. LTD.                #
#                       All rights reserved                          #
#                                                                    #
#--------------------------------------------------------------------#

# Import modules
import os
import glob
import ctypes
import sys
import subprocess
import shutil
import zipfile

APP_NAME = "TINT_App"
INSTALL_NAME = "Install_TINT"
CONFIG_SOURCE = os.path.join(os.getcwd(), "config")
DATA_SOURCE = os.path.join(os.getcwd(), "data")
DOCS_SOURCE = os.path.join(os.getcwd(), "docs")

DIST_DIR = os.path.join(os.getcwd(), "dist")
SED_DIR = r"C:\Local" # requires a directory without space to work correctly
APP_DIR = os.path.join(DIST_DIR, APP_NAME)
CONFIG_DEST = os.path.join(DIST_DIR, APP_NAME, "config")
DATA_DEST = os.path.join(DIST_DIR, APP_NAME, "data")
DOCS_DEST = os.path.join(DIST_DIR, APP_NAME, "docs")


def check_sed():
    sed_ls = glob.glob(os.path.join(DIST_DIR, "*.SED"))
    if len(sed_ls) == 1:
        print(f"Found an SED file - {sed_ls[0]}")
        with open(sed_ls[0], 'r') as f:
            sed_str = f.read()
        sed_exist = True
        sed_filename = os.path.basename(sed_ls[0])
        print("Existence set to True, file string copied")
        return sed_exist, sed_filename, sed_str
    else:
        return False, "", ""

def clear_scraps():
    '''Check for scraps and deletes them'''
    scraps = ["build", "dist", APP_NAME + ".spec", INSTALL_NAME + ".spec"]

    for scrap in scraps:
        try:
            full_scrap = os.path.join(os.getcwd(), scrap)
            if os.path.isfile(full_scrap):
                print(f"[{full_scrap}] is a file")
                os.remove(full_scrap)
            elif os.path.isdir(full_scrap):
                print(f"[{full_scrap}] is a directory")
                shutil.rmtree(full_scrap)
            else:
                print(f"[{full_scrap}] is not file nor directory")
        except Exception as e:
            print(f"Error when checking {full_scrap} - {e}")

def make_app_exe():
    # Call PyInstaller actions
    subprocess.check_output(
        f"pyinstaller --icon=config/assets/mw_truck.ico --noconsole {APP_NAME}.py", shell=True)

    print("APP EXE Conversion complete. Start asset transfer")
    # Copy config folder into distribution
    try:
        shutil.copy(os.path.join(CONFIG_SOURCE, "assets", "mw_truck.ico"), os.path.join(DIST_DIR, "mw_truck.ico"))
        shutil.copytree(CONFIG_SOURCE, CONFIG_DEST)
        print("Copied configuration folder into dist App folder")
        os.remove(os.path.join(CONFIG_DEST, "systemconfig.xml"))
        shutil.copytree(DATA_SOURCE, DATA_DEST)
        print("Copied data folder into dist App folder")
        for f in glob.glob(os.path.join(DATA_DEST, "*.csv")):
            if not "Empty" in f:
                print(f"Removing {f}")
                os.remove(f)
        for f in glob.glob(os.path.join(DATA_DEST, "*.csv")):
            print(f"Renaming {f} to {f.replace(' - Empty', '')}")
            os.rename(f, f.replace(" - Empty", ""))
        shutil.copytree(DOCS_SOURCE, DOCS_DEST)
        print("Copied docs folder into dist App folder")
    except Exception as e:
        print(f"Error copying Config folder - {e}")

    print("Start archiving App")
    shutil.make_archive(f"{APP_DIR}_Package", "zip", APP_DIR)
    print("Complete archive App")

def make_install_exe():
    # Call PyInstaller actions
    subprocess.check_output(
        f"pyinstaller --icon=config/assets/mw_truck.ico --onefile --noconsole {INSTALL_NAME}.py", shell=True)

    print("Install EXE Conversion complete")

def make_install_package(sed_exist=False, sed_filename="", sed_str=""):
    '''create iexpress installation package'''
    if sed_exist:
        print(f"SED file exists - creating SED file")
        sed_filepath = os.path.join(DIST_DIR, sed_filename)
        with open(sed_filepath, 'w') as fw:
            fw.write(sed_str)
        fw.close()
        sed_filepath = os.path.join(SED_DIR, sed_filename)
        with open(sed_filepath, 'w') as fw:
            fw.write(sed_str)
        fw.close()
        if os.path.isfile(sed_filepath):
            print(f"SED File is reading in - {sed_filepath}")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "iexpress", r"/N {}".format(sed_filepath), None, 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "iexpress", None, None, 1)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "iexpress", None, None, 1)

def main():
    sed_exist, sed_filename, sed_str = check_sed()
    clear_scraps()
    make_app_exe()
    make_install_exe()
    make_install_package(sed_exist, sed_filename, sed_str)
    sys.exit()

if __name__ == "__main__":
    main()
