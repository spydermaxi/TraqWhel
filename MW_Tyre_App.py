#!/usr/bin/env python3
#-----------------------------------------------------------------------------#
#                                                                             #
#                            Python script                                    #
#                                                                             #
#-----------------------------------------------------------------------------#
#
# Ident        : ProMon_Setup.py
__version__ = "0.0.1"
__author__ = "Adrian Loo"
"""
The Tyre App for tracking tyre usage and inventory for Modern Wong
"""
#
# History
# 2021-09-29: v0.0.1 [Adrian Loo] Development start
# 2021-09-29: v0.0.1 [Adrian Loo] Complete StartPage
# 2021-09-30: v0.0.1 [Adrian Loo] Fix page size and position
# 2021-10-01: v0.0.1 [Adrian Loo] Complete Track Inventory Page
#
#-----------------------------------------------------------------------------#
#                                                                             #
#                  Copyright (c) 2021, AXONBOTS PTE. LTD.                     #
#                           All rights reserved                               #
#                                                                             #
#-----------------------------------------------------------------------------#

# Import Modules

import os
import sys
import re
import shutil
import random
import logging
from datetime import datetime

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox
from tkinter import simpledialog as tkSimpleDialog

# ----- Methods ----- #

LARGE_FONT = ("Verdana", 12, "bold")
LB_FONT = ("Verdana", 11, "bold")
RB_FONT = ("Verdana", 10)


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
    log_dir = os.path.join(os.getcwd(), "Logs")

    # setup logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s\t[%(funcName)s][%(levelname)s]:\t%(message)s')

    file_handler = logging.FileHandler(os.path.join(log_dir, '{}_{}.log'.format(
        os.path.basename(basefile).split(".")[0], str(datetime.now().date()))))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("Logging initialized")

    logger.info(
        "Running from base file - {}, version: {}".format(os.path.basename(basefile), version))

    file_handler.setLevel(loglevel)

    return logger


class TyreApp(tk.Tk):
    '''
    Main GUI interface for MW Tyre App

    Initiation codes
    app = TyreApp()
    app.mainloop()
    '''

    def __init__(self, *args, **kwargs):

        main_ver = __version__

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default='Config\\mw_truck.ico')
        tk.Tk.wm_title(
            self, "Modern Wong Transport Tyre Inventory and Tracking - {}".format(main_ver))

        self.geometry("1220x720+10+10")
        self.minsize(1016, 600)

        style = ttk.Style(self)
        style.configure("TRadiobutton", font=RB_FONT)
        style.configure("TLabelframe.Label", foreground='black', font=LB_FONT)

        logger.info("Application initialized")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, TrackTyrePage, TrackInvPage, DashboardPage):

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.start_frame(StartPage)

        self.protocol('WM_DELETE_WINDOW', self.on_exit)

    def start_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()
        logger.info("Show frame - {}".format(cont))
        logger.info("Application initialized")

    def show_frame(self, dst_cont):

        frame = self.frames[dst_cont]
        frame.tkraise()
        logger.info("Show frame - {}".format(dst_cont))

    def on_exit(self):
        if tkMessageBox.askyesno('System Warning', 'Do you want to quit the application?'):
            logger.info("User terminate application")
            self.destroy()
            exit()
        else:
            pass


class StartPage(tk.Frame):
    '''
    The initialize page of the app with 3 selections
    '''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=str(controller.winfo_height()-20), width=str(controller.winfo_width()-20))
        self.grid(column='0', row='0', sticky='n')

        self.header_lbl = ttk.Label(self)
        self.header_lbl.configure(font='{Source Sans Pro} 32 {bold}',
                                  justify='center', text='Modern Wong Tyre & Inventory Tracking')
        self.header_lbl.place(anchor='n', relx='0.5', rely='0.1')

        self.track_tyre_lbl = ttk.Label(self)
        self.track_tyre_lbl.configure(
            font='{source sans pro} 18 {bold}', justify='center', text='Track\nTyre')
        self.track_tyre_lbl.place(anchor='n', relx='0.3', rely='0.3')

        self.track_inv_lbl = ttk.Label(self)
        self.track_inv_lbl.configure(
            font='{source sans pro} 18 {bold}', justify='center', text='Track\nInventory')
        self.track_inv_lbl.place(anchor='n', relx='0.5', rely='0.3')

        self.dashboard_lbl = ttk.Label(self)
        self.dashboard_lbl.configure(
            font='{source sans pro} 18 {bold}', justify='center', text='Launch\nDashboard')
        self.dashboard_lbl.place(anchor='n', relx='0.7', rely='0.3')

        self.track_tyre_btn = ttk.Button(
            self, command=lambda: controller.show_frame(TrackTyrePage))
        self.mw_blue_truck_png = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "Config", 'mw_blue_truck.png'))
        self.track_tyre_btn.configure(
            image=self.mw_blue_truck_png, text='Track Tyre')
        self.track_tyre_btn.place(
            anchor='n', height='140', width='140', relx='0.3', rely='0.4')

        self.track_inv_btn = ttk.Button(
            self, command=lambda: controller.show_frame(TrackInvPage))
        self.mw_green_truck_png = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "Config", 'mw_green_truck.png'))
        self.track_inv_btn.configure(
            image=self.mw_green_truck_png, text='Track Inventory')
        self.track_inv_btn.place(
            anchor='n', height='140', width='140', relx='0.5', rely='0.4')

        self.launch_db_btn = ttk.Button(
            self, command=lambda: controller.show_frame(DashboardPage))
        self.mw_white_truck_png = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "Config", 'mw_white_truck.png'))
        self.launch_db_btn.configure(
            image=self.mw_white_truck_png, text='Launch Dashboard')
        self.launch_db_btn.place(
            anchor='n', height='140', width='140', relx='0.7', rely='0.4')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.5', rely='0.9')


class TrackTyrePage(tk.Frame):
    '''
    The tyre tracking interface page of the app
    '''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=str(controller.winfo_height()-20), width=str(controller.winfo_width()-20))
        self.grid(column='0', row='0', sticky='n')

        self.header_lbl = ttk.Label(self)
        self.header_lbl.configure(font='{Source Sans Pro} 20 {bold}',
                                  justify='center', text='Tyre Tracking')
        self.header_lbl.place(anchor='n', relx='0.5', rely='0.01')



        self.back_btn = ttk.Button(self, text="Back", width=20, command=lambda: controller.show_frame(StartPage))
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.9', rely='0.95')


class TrackInvPage(tk.Frame):
    '''
    The inventory tracking interface page of the app
    '''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=str(controller.winfo_height()-20), width=str(controller.winfo_width()-20))
        self.grid(column='0', row='0', sticky='n')

        self.header_lbl = ttk.Label(self)
        self.header_lbl.configure(font='{Source Sans Pro} 20 {bold}',
                                  justify='center', text='Tyre Inventory Tracking')
        self.header_lbl.place(anchor='n', relx='0.5', rely='0.01')

        self.inv_sum_lbf = ttk.Labelframe(self)
        self.inv_sum_lbf.configure(labelanchor='n', text='Tyre Inventory Summary')
        self.inv_sum_lbf.place(anchor='n', relheight='0.85', relwidth='0.48', relx='0.25', rely='0.06', x='0', y='0')

        self.cur_inv_lbf = ttk.Labelframe(self.inv_sum_lbf)
        self.cur_inv_lbf.configure(text='Current Inventory')
        self.cur_inv_lbf.place(anchor='n', relheight='0.35', relwidth='0.95', relx='0.5', rely='0.01', x='0', y='0')

        self.refresh_btn = ttk.Button(self.inv_sum_lbf, command=self.update_inv_trend)
        self.refresh_btn.configure(text='Refresh')
        self.refresh_btn.place(anchor='nw', relheight='0.05', relwidth='0.2', relx='0.03', rely='0.38', x='0', y='0')

        self.fig = plt.figure(1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.inv_sum_lbf)
        self.plot_widget = self.canvas.get_tk_widget()
        self.plot_widget.place(anchor='n', relheight='0.52', relwidth='0.95', relx='0.5', rely='0.45')
        self.update_inv_trend()

        self.inv_input_lbf = ttk.Labelframe(self)
        self.inv_input_lbf.configure(labelanchor='n', text='Input Data')
        self.inv_input_lbf.place(anchor='n', relheight='0.85', relwidth='0.48', relx='0.75', rely='0.06', x='0', y='0')

        self.tyre_name_lbl = ttk.Label(self.inv_input_lbf)
        self.tyre_name_lbl.configure(font='{source sans pro} 18 {bold}', justify='right', text='Tyre Name: ')
        self.tyre_name_lbl.place(anchor='ne', relx='0.4', rely='0.1', x='0', y='0')

        self.tyre_qty_lbl = ttk.Label(self.inv_input_lbf)
        self.tyre_qty_lbl.configure(font='{source sans pro} 18 {bold}', justify='right', text='Quantity: ')
        self.tyre_qty_lbl.place(anchor='ne', relx='0.4', rely='0.2', x='0', y='0')

        self.cost_lbl = ttk.Label(self.inv_input_lbf)
        self.cost_lbl.configure(font='{source sans pro} 18 {bold}', justify='right', text='Cost/Unit: ')
        self.cost_lbl.place(anchor='ne', relx='0.4', rely='0.3', x='0', y='0')

        self.total_cost_lbl = ttk.Label(self.inv_input_lbf)
        self.total_cost_lbl.configure(font='{source sans pro} 18 {bold}', justify='right', text='Total Cost: ')
        self.total_cost_lbl.place(anchor='ne', relx='0.4', rely='0.4', x='0', y='0')

        self.tyre_name_entry = ttk.Entry(self.inv_input_lbf)
        self.tyre_name_entry.configure(cursor='hand2', font='{source sans pro} 16 {}')
        _text_ = '''Enter Product Name'''
        self.tyre_name_entry.delete('0', 'end')
        self.tyre_name_entry.insert('0', _text_)
        self.tyre_name_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.1', x='0', y='0')

        self.qty_entry = ttk.Entry(self.inv_input_lbf)
        self.qty_entry.configure(cursor='hand2', font='{source sans pro} 16 {}')
        _text_ = '''Enter Quantity'''
        self.qty_entry.delete('0', 'end')
        self.qty_entry.insert('0', _text_)
        self.qty_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.2', x='0', y='0')

        self.cost_entry = ttk.Entry(self.inv_input_lbf)
        self.cost_entry.configure(cursor='hand2', font='{source sans pro} 16 {}')
        _text_ = '''Enter Cost Per Unit'''
        self.cost_entry.delete('0', 'end')
        self.cost_entry.insert('0', _text_)
        self.cost_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.3', x='0', y='0')

        self.total_cost_entry = ttk.Entry(self.inv_input_lbf)
        self.total_cost_entry.configure(cursor='hand2', font='{source sans pro} 16 {}', state='readonly')
        _text_ = '''Total Cost'''
        self.total_cost_entry['state'] = 'normal'
        self.total_cost_entry.delete('0', 'end')
        self.total_cost_entry.insert('0', _text_)
        self.total_cost_entry['state'] = 'readonly'
        self.total_cost_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.4', x='0', y='0')

        self.submit_btn = ttk.Button(self.inv_input_lbf)
        self.submit_btn.configure(text='Submit Entry')
        self.submit_btn.place(anchor='n', relheight='0.1', relwidth='0.3', relx='0.5', rely='0.5', x='0', y='0')

        self.download_btn = ttk.Button(self.inv_input_lbf)
        self.download_btn.configure(text='Download All Data')
        self.download_btn.place(anchor='n', relheight='0.1', relwidth='0.3', relx='0.5', rely='0.65', x='0', y='0')

        self.back_btn = ttk.Button(self, text="Back", width=20, command=lambda: controller.show_frame(StartPage))
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.9', rely='0.95')

    def update_inv_trend(self):
        plt.ion()
        t = np.arange(0.0,random.random(),0.01)
        s = np.sin(np.pi*t)
        plt.plot(t,s)
        self.fig.canvas.draw()

class DashboardPage(tk.Frame):
    '''
    The dashboard page of the app
    '''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(height=str(controller.winfo_height()-20), width=str(controller.winfo_width()-20))
        self.grid(column='0', row='0', sticky='n')

        self.header_lbl = ttk.Label(self)
        self.header_lbl.configure(font='{Source Sans Pro} 20 {bold}',
                                  justify='center', text='Dashboard Overview')
        self.header_lbl.place(anchor='n', relx='0.5', rely='0.01')



        self.back_btn = ttk.Button(self, text="Back", width=20, command=lambda: controller.show_frame(StartPage))
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.9', rely='0.95')


# ----- Execution ----- #


if __name__ == "__main__":

    # Create logger
    logger = create_logger(__name__, __file__, __version__, 10)

    # Launch App
    app = TyreApp()
    app.mainloop()
