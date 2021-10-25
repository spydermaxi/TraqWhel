#!/usr/bin/env python3
#--------------------------------------------------------------------#
#                                                                    #
#                        Python script                               #
#                                                                    #
#--------------------------------------------------------------------#
#
# Ident        : Install_TINT.py
__version__ = "1.0.0"
__author__ = "Adrian Loo"

__license__ = '''BSD 3-Clause License

Copyright (c) 2021, AXONBOTS Pte Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or withoutmodification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'''

"""
Installation app for TINT App
"""
#
# History
# 2021-10-25: 1.0.0 [Adrian Loo] Create install sequence, UI and functions
#
#--------------------------------------------------------------------#
#                                                                    #
#                       BSD 3-Clause License                         #
#              Copyright (c) 2021, AXONBOTS PTE. LTD.                #
#                       All rights reserved                          #
#                                                                    #
#--------------------------------------------------------------------#

# Import modules
import os, sys, subprocess, glob, shutil, logging, win32com.client
from datetime import datetime, timedelta

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox
from tkinter import simpledialog as tkSimpleDialog
import warnings
warnings.filterwarnings("ignore")

# ----- Methods ----- #

LARGE_FONT = ("Verdana", 12, "bold")
LB_FONT = ("Verdana", 11, "bold")
RB_FONT = ("Verdana", 10)

APP_NAME = "TINT_App"
for PACKAGE_SOURCE in glob.glob(os.path.join(os.getcwd(), "*.ZIP")):
    break
CONFIG_SOURCE = os.path.join(os.getcwd(), "config")
ASSETS_SOURCE = os.path.join(CONFIG_SOURCE, "assets")
LOG_SOURCE = os.path.join(os.getcwd(), "logs")


def create_logger(name, basefile, version, loglevel):
    '''
    Method to create logger
    name: usually refers to the variable __name__
    basefile: usually refers to the __file__
    version: usually refers to the __version__
    loglevel: integer representing the logging level
        Level       Numeric value
        CRITICAL    50
        ERROR       40
        WARNING     30
        INFO        20
        DEBUG       10
        NOTSET      0
    '''
    # Create log directory
    try:
        os.mkdir(LOG_SOURCE)
    except Exception as e:
        pass

    # setup logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s\t[%(funcName)s][%(levelname)s]:\t%(message)s')

    file_handler = logging.FileHandler(os.path.join(LOG_SOURCE, f'{os.path.basename(basefile).split(".")[0]}_{str(datetime.now().date())}.log'))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("Logging initialized")

    logger.info(f"Running from base file - {os.path.basename(basefile)}, version: {version}")

    file_handler.setLevel(loglevel)

    return logger


class InstallTint(tk.Tk):
    '''Installation GUI for TINT App'''

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        try:
            tk.Tk.iconbitmap(self, default='mw_truck.ico')
        except Exception as e:
            logger.exception(f"Error loading icon - {e}")
        tk.Tk.wm_title(self, "Install TINT [Tyre Inventory & Tracking] - {} (by AxonBots Pte Ltd)".format(__version__))

        # -- Position the window on cneter of screen -- #
        self.update_idletasks()
        width = 480
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = 320
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.deiconify()
        self.resizable(False, False)

        style = ttk.Style(self)
        logger.info("Theme in use - {}".format(style.theme_use()))
        style.configure("TRadiobutton", font=RB_FONT)
        style.configure("TLabelframe.Label", foreground='black', font=LB_FONT)

        logger.info("Application initialized")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.default_path = os.path.join(os.path.expanduser("~"), APP_NAME)
        self.frames = {}

        for F in (StartPage, ProgressPage, CompletePage):

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        self.protocol('WM_DELETE_WINDOW', self.on_exit)

    def show_frame(self, dst_cont):

        frame = self.frames[dst_cont]
        frame.tkraise()
        logger.info("Show frame - {}".format(dst_cont))

    def on_exit(self):
        if tkMessageBox.askyesno('System Warning', 'Do you want to quit installation?'):
            logger.info("User terminate application")
            self.destroy()
            sys.exit()
        else:
            pass


class StartPage(tk.Frame):
    '''
    The initialize page of the installation app.
    Welcome and License Page
    '''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=str(controller.winfo_height()-20), width=str(controller.winfo_width()-20))
        self.grid(column='0', row='0')

        self.strpg_head_lbl = ttk.Label(self)
        self.strpg_head_lbl.configure(font='{source sans pro} 12 {bold}', justify='left', text='Install TINT - Tyre Inventory and Tracking App')
        self.strpg_head_lbl.place(anchor='n', relx='0.5', rely='0.065', x='0', y='0')
        self.strpg_subtitle_lbl = ttk.Label(self)
        self.strpg_subtitle_lbl.configure(font='{source sans pro} 10 {}', text='Choose Install now to start installation using default settings,\nor choose Customize to set a different location.')
        self.strpg_subtitle_lbl.place(anchor='n', relx='0.5', rely='0.15', x='0', y='0')

        self.install_now_btn = ttk.Button(self, command=lambda: self.install_now(controller.default_path))
        self.install_now_btn.configure(text=f'Install Now\n{controller.default_path}')
        self.install_now_btn.place(anchor='n', relheight='0.2', relwidth='0.7', relx='0.5', rely='0.3', x='0', y='0')

        self.custom_install_btn = ttk.Button(self, command=self.install_custom)
        self.custom_install_btn.configure(text='Customize Installation\nChoose Location')
        self.custom_install_btn.place(anchor='n', relheight='0.2', relwidth='0.7', relx='0.5', rely='0.55', x='0', y='0')

        self.cancel_btn = ttk.Button(self, command=lambda: controller.on_exit())
        self.cancel_btn.configure(text='Cancel')
        self.cancel_btn.place(anchor='se', relwidth='0.2', relx='0.9', rely='0.95', x='0', y='0')

        self.controller = controller
        self.parent = parent

    def install_now(self, install_path):
        '''Execute Installation on default path'''
        self.controller.default_path = install_path
        logger.info(f"User selected install path - {self.controller.default_path}")
        self.controller.show_frame(ProgressPage)

    def install_custom(self):
        '''Execute Installation on user defined install path'''
        logger.info("User selected custom install path")
        install_path = tkFileDialog.askdirectory(title="Select Directory to install")
        if os.path.isdir(install_path):
            self.controller.default_path = os.path.join(os.path.normpath(install_path), APP_NAME)
            logger.info(f"User selected path - {self.controller.default_path}")
            self.controller.show_frame(ProgressPage)
        else:
            logger.info(f"Unable to proceed. Operation was cancelled - {install_path}")
            tkMessageBox.showerror("Error", "No Path selected or Operation cancelled")


class ProgressPage(tk.Frame):
    '''
    The initialize page of the installation app.
    Welcome and License Page
    '''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=str(controller.winfo_height()-20), width=str(controller.winfo_width()-20))
        self.grid(column='0', row='0')

        logger.info(f"User Start installation on {controller.default_path}")

        self.prgpg_head_lbl = ttk.Label(self)
        self.prgpg_head_lbl.configure(font='{source sans pro} 12 {bold}', justify='left', text='Installing TINT - Tyre Inventory and Tracking App')
        self.prgpg_head_lbl.place(anchor='n', relx='0.5', rely='0.065', x='0', y='0')

        self.prg_box = tk.Text(self)
        self.prg_box.configure(height='10', width='46', wrap='word')
        _starttext_ = f'Selected install path\n==================\n{controller.default_path}\n==================\n\nClick "Next" to continue installation'
        self.prg_box.insert('0.0', _starttext_)
        self.prg_box.place(anchor='n', relx='.5', rely='.2', relheight='.6')

        yscroll = tk.Scrollbar(self, command=self.prg_box.yview)
        yscroll.place(anchor='n', relx='.9', rely='.2', relheight='.6')
        self.prg_box.configure(yscrollcommand=yscroll.set)

        self.back_btn = ttk.Button(self, command=None)
        self.back_btn.configure(text='Back', state='disabled')
        self.back_btn.place(anchor='se', relwidth='0.2', relx='0.3', rely='0.95', x='0', y='0')

        self.next_btn = ttk.Button(self, command=self.next)
        self.next_btn.configure(text='Next')
        self.next_btn.place(anchor='se', relwidth='0.2', relx='0.6', rely='0.95', x='0', y='0')

        self.cancel_btn = ttk.Button(self, command=lambda: controller.on_exit())
        self.cancel_btn.configure(text='Cancel')
        self.cancel_btn.place(anchor='se', relwidth='0.2', relx='0.9', rely='0.95', x='0', y='0')

        self.controller = controller
        self.unpacked = False

    def next(self):
        if self.unpacked:
            pass
        else:
            self.unpack_check()
        self.controller.show_frame(CompletePage)

    def update_progress(self, message):
        '''Updates information in progress box'''
        logger.info(message)
        message = f"{datetime.now()}: {message}"
        self.prg_box.insert(tk.END, message + "\n")

    def unpack_check(self):
        '''unpacks archive into target destination and check list of files'''
        self.update_progress("Commence Installation")
        try:
            self.update_progress(f"Unpacking to destination - {self.controller.default_path}")

            shutil.unpack_archive(PACKAGE_SOURCE, self.controller.default_path, "zip")
            self.update_progress("Package unpacked")
            self.update_progress("Creating Desktop Shortcut")
            shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", f"{APP_NAME}.lnk")
            target_path = os.path.join(self.controller.default_path, f"{APP_NAME}.exe")
            icon = os.path.join(self.controller.default_path, "config", "assets", "mw_truck.ico")

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = self.controller.default_path
            shortcut.IconLocation = icon
            shortcut.save()
            self.update_progress("Desktop Shortcut created")

            self.unpacked = True
        except Exception as e:
            err_msg = f"Error unpacking Archive - {e}"
            self.update_progress(err_msg)
            logger.exception(err_msg)

        if self.unpacked:
            self.update_progress("Checking files")
            # for root, sub, files in os.walk(self.controller.default_path):
            #     for f in files:
            #         self.update_progress(os.path.join(root, f).replace(self.controller.default_path, ""))
            self.next_btn.configure(state='normal')
            self.update_progress("File Check Complete. Installation success")
            self.controller.show_frame(CompletePage)
        else:
            tkMessageBox.showerror("Error", "Error during installation\nPlease contact developer")


class CompletePage(tk.Frame):
    '''
    The initialize page of the installation app.
    Welcome and License Page
    '''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=str(controller.winfo_height()-20), width=str(controller.winfo_width()-20))
        self.grid(column='0', row='0')

        self.compg_head_lbl = ttk.Label(self)
        self.compg_head_lbl.configure(font='{source sans pro} 12 {bold}', justify='left', text='TINT Installation Complete')
        self.compg_head_lbl.place(anchor='n', relx='0.5', rely='0.065', x='0', y='0')

        self.launch_btn = ttk.Button(self, command=self.launch_app)
        self.launch_btn.configure(text=f"Exit & Launch {APP_NAME}")
        self.launch_btn.place(anchor='n', relwidth='.3', relheight='.2', relx='0.5', rely='0.3')

        self.back_btn = ttk.Button(self, command=lambda: controller.show_frame(ProgressPage))
        self.back_btn.configure(text='Back')
        self.back_btn.place(anchor='se', relwidth='0.2', relx='0.3', rely='0.95', x='0', y='0')

        self.next_btn = ttk.Button(self, command=lambda: controller.on_exit())
        self.next_btn.configure(text='Next', state='disabled')
        self.next_btn.place(anchor='se', relwidth='0.2', relx='0.6', rely='0.95', x='0', y='0')

        self.cancel_btn = ttk.Button(self, command=lambda: controller.on_exit())
        self.cancel_btn.configure(text='Finish')
        self.cancel_btn.place(anchor='se', relwidth='0.2', relx='0.9', rely='0.95', x='0', y='0')

        self.controller = controller

    def launch_app(self):
        os.chdir(self.controller.default_path)
        os.startfile(APP_NAME + ".exe")
        self.controller.destroy()
        sys.exit()


# ----- Execution ----- #


if __name__ == "__main__":

    # Create logger
    logger = create_logger(__name__, __file__, __version__, 10)

    # Launch App
    app = InstallTint()
    app.mainloop()
