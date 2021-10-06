import os, sys, subprocess, shutil

BATFILE = "Run_Convert.bat"
APP = "MW_Tyre_App"
CONFIG = "Config"
DATA = "Data"

# Check for scraps
scraps = ["build", "dist", APP + ".spec"]

for scrap in scraps:
    try:
        full_scrap = os.path.join(os.getcwd(), scrap)
        if os.path.isfile(full_scrap):
            print("[{}] is a file".format(full_scrap))
            os.remove(full_scrap)
        elif os.path.isdir(full_scrap):
            print("[{}] is a directory".format(full_scrap))
            shutil.rmtree(full_scrap)
        else:
            print("[{}] is not file nor directory".format(full_scrap))
    except Exception as e:
        print("Error when checking {} - {}".format(full_scrap, e))

# Call PyInstaller actions
subprocess.call([os.path.join(os.getcwd(), BATFILE)])

# Copy config folder into distribution
try:
    shutil.copytree(os.path.join(os.getcwd(), CONFIG), os.path.join(os.getcwd(), "dist", APP, CONFIG))
    print("Copied configuration folder into dist App folder")
    shutil.copytree(os.path.join(os.getcwd(), DATA), os.path.join(os.getcwd(), "dist", APP, DATA))
    print("Copied data folder into dist App folder")
except Exception as e:
    print("Error copying Config folder - {}".format(e))

# Create bat file to execute exe
try:
    with open(os.path.join(os.getcwd(), "dist", "Start_App.bat"), "w") as b:
        b.writelines("@ECHO OFF\n cd {}\n{}.exe".format(APP, APP))
    b.close()
    print("Create Bat Exe file")
except Exception as e:
    print("Error happend when doing Batch file creating for app execution - {}".format(e))

input("Complete Build")
