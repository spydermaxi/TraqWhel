#!/usr/bin/env python3
#--------------------------------------------------------------------#
#                                                                    #
#                        Python script                               #
#                                                                    #
#--------------------------------------------------------------------#
#
# Ident        : Build_exe.py
__version__ = "1.0.0"
__author__ = "axonspyder"
"""
Build_exe.py is built for easy CI of the target app
"""
#
#
#--------------------------------------------------------------------#
#                                                                    #
#                       BSD 3-Clause License                         #
#              Copyright (c) 2021, AXONBOTS PTE. LTD.                #
#                       All rights reserved                          #
#                                                                    #
#--------------------------------------------------------------------#

# Import modules
import os, sys, subprocess, shutil

APP_NAME = "TINT_App"
CONFIG_SOURCE = os.path.join(os.getcwd(), "config")
DATA_SOURCE = os.path.join(os.getcwd(), "data")
DOCS_SOURCE = os.path.join(os.getcwd(), "docs")

CONFIG_DEST = os.path.join(os.getcwd(), "dist", APP_NAME, "config")
DATA_DEST = os.path.join(os.getcwd(), "dist", APP_NAME, "data")
DOCS_DEST = os.path.join(os.getcwd(), "dist", APP_NAME, "docs")

def clear_scraps():
    '''Check for scraps and deletes them'''
    scraps = ["build", "dist", APP_NAME + ".spec"]

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

def make_exe():
    # Call PyInstaller actions
    subprocess.check_output(f"pyinstaller --icon=config/mw_truck.ico --noconsole {APP_NAME}.py", shell=True)

    print("Conversion complete. Start asset transfer")
    # Copy config folder into distribution
    try:
        shutil.copytree(CONFIG_SOURCE, CONFIG_DEST)
        print("Copied configuration folder into dist App folder")
        shutil.copytree(DATA_SOURCE, DATA_DEST)
        print("Copied data folder into dist App folder")
        shutil.copytree(DOCS_SOURCE, DOCS_DEST)
        print("Copied docs folder into dist App folder")
    except Exception as e:
        print(f"Error copying Config folder - {e}")

    # Create bat file to execute exe [deprecate]
    # try:
    #     with open(os.path.join(os.getcwd(), "dist", "Start_App.bat"), "w") as b:
    #         b.writelines("@ECHO OFF\n cd {}\n{}.exe".format(APP, APP))
    #     b.close()
    #     print("Create Bat Exe file")
    # except Exception as e:
    #     print("Error happend when doing Batch file creating for app execution - {}".format(e))

def main():
    clear_scraps()
    make_exe()

if __name__ == "__main__":
    main()
