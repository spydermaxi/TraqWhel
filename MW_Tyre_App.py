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
# 2021-10-02: v0.0.1 [Adrian Loo] Complete Track Inventory Page functions
# 2021-10-04: v0.0.1 [Adrian Loo] Complete Dashboard Page, functions and visualization
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
import calendar
from datetime import datetime, timedelta

import matplotlib
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
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

DATA_SOURCE = os.path.join(os.getcwd(), "Data")

INV_FILE_NAME = "tyre_inventory_db.csv"
INV_DB = os.path.join(DATA_SOURCE, INV_FILE_NAME)

INV_IN_FILE_NAME = "tyre_inventory_in_db.csv"
INV_IN_DB = os.path.join(DATA_SOURCE, INV_IN_FILE_NAME)

TRACK_FILE_NAME = "tyre_tracking_db.csv"
TRACK_DB = os.path.join(DATA_SOURCE, TRACK_FILE_NAME)


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
    try:
        os.mkdir(log_dir)
    except Exception as e:
        pass

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

        self.currency = "RM"

        self.header_lbl = ttk.Label(self)
        self.header_lbl.configure(font='{Source Sans Pro} 20 {bold}',
                                  justify='center', text='Tyre Inventory Tracking')
        self.header_lbl.place(anchor='n', relx='0.5', rely='0.01')

        self.inv_sum_lbf = ttk.Labelframe(self)
        self.inv_sum_lbf.configure(labelanchor='n', text='Tyre Inventory Summary')
        self.inv_sum_lbf.place(anchor='n', relheight='0.88', relwidth='0.48', relx='0.25', rely='0.06', x='0', y='0')

        self.cur_inv_lbf = ttk.Labelframe(self.inv_sum_lbf)
        self.cur_inv_lbf.configure(text='Current Inventory')
        self.cur_inv_lbf.place(anchor='n', relheight='0.3', relwidth='0.95', relx='0.5', rely='0.01', x='0', y='0')

        self.refresh_btn = ttk.Button(self.inv_sum_lbf, command=self.update_inv_trend)
        self.refresh_btn.configure(text='Refresh')
        self.refresh_btn.place(anchor='nw', relheight='0.05', relwidth='0.2', relx='0.03', rely='0.32', x='0', y='0')

        self.fig, self.ax = plt.subplots(tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.inv_sum_lbf)
        self.plot_widget = self.canvas.get_tk_widget()
        self.plot_widget.place(anchor='n', relheight='0.57', relwidth='0.95', relx='0.5', rely='0.38')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(self.canvas, self.inv_sum_lbf, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.95', relx='0.5', rely='0.94')
        self.update_inv_trend()

        self.inv_input_lbf = ttk.Labelframe(self)
        self.inv_input_lbf.configure(labelanchor='n', text='Input Data')
        self.inv_input_lbf.place(anchor='n', relheight='0.88', relwidth='0.48', relx='0.75', rely='0.06', x='0', y='0')

        self.tyre_name_lbl = ttk.Label(self.inv_input_lbf)
        self.tyre_name_lbl.configure(font='{source sans pro} 18 {bold}', justify='right', text='Tyre Name: ')
        self.tyre_name_lbl.place(anchor='ne', relx='0.4', rely='0.1', x='0', y='0')

        self.tyre_qty_lbl = ttk.Label(self.inv_input_lbf)
        self.tyre_qty_lbl.configure(font='{source sans pro} 18 {bold}', justify='right', text='Quantity: ')
        self.tyre_qty_lbl.place(anchor='ne', relx='0.4', rely='0.2', x='0', y='0')

        self.cost_lbl = ttk.Label(self.inv_input_lbf)
        self.cost_lbl.configure(font='{source sans pro} 18 {bold}', justify='right', text='Cost/Unit ({}): '.format(self.currency))
        self.cost_lbl.place(anchor='ne', relx='0.4', rely='0.3', x='0', y='0')

        self.total_cost_lbl = ttk.Label(self.inv_input_lbf)
        self.total_cost_lbl.configure(font='{source sans pro} 18 {bold}', justify='right', text='Total Cost ({}): '.format(self.currency))
        self.total_cost_lbl.place(anchor='ne', relx='0.4', rely='0.4', x='0', y='0')

        self.tyre_name_entry = ttk.Entry(self.inv_input_lbf)
        self.tyre_name_entry.configure(foreground = 'grey', cursor='hand2', font='{source sans pro} 16 {}')
        self._tyre_name_text_ = '''Enter Product Name'''
        self.tyre_name_entry.delete('0', 'end')
        self.tyre_name_entry.insert('0', self._tyre_name_text_)
        self.tyre_name_entry.bind('<FocusIn>', self.on_tyre_name_entry_click)
        self.tyre_name_entry.bind('<FocusOut>', self.on_tyre_name_entry_focus_out)
        self.tyre_name_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.1', x='0', y='0')

        self.qty_entry = ttk.Entry(self.inv_input_lbf)
        self.qty_entry.configure(foreground = 'grey', cursor='hand2', font='{source sans pro} 16 {}')
        self.qty_text_ = '''Enter Quantity'''
        self.qty_entry.delete('0', 'end')
        self.qty_entry.insert('0', self.qty_text_)
        self.qty_entry.bind('<FocusIn>', self.on_qty_entry_click)
        self.qty_entry.bind('<FocusOut>', self.on_qty_entry_focus_out)
        self.qty_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.2', x='0', y='0')

        self.cost_entry = ttk.Entry(self.inv_input_lbf)
        self.cost_entry.configure(foreground = 'grey', cursor='hand2', font='{source sans pro} 16 {}')
        self.cost_text_ = '''Enter Cost Per Unit'''
        self.cost_entry.delete('0', 'end')
        self.cost_entry.insert('0', self.cost_text_)
        self.cost_entry.bind('<FocusIn>', self.on_cost_entry_click)
        self.cost_entry.bind('<FocusOut>', self.on_cost_entry_focus_out)
        self.cost_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.3', x='0', y='0')

        self.total_cost_entry = ttk.Entry(self.inv_input_lbf)
        self.total_cost_entry.configure(cursor='hand2', font='{source sans pro} 16 {}', state='readonly')
        self.total_cost_text_ = '''Total Cost'''
        self.total_cost_entry['state'] = 'normal'
        self.total_cost_entry.delete('0', 'end')
        self.total_cost_entry.insert('0', self.total_cost_text_)
        self.total_cost_entry['state'] = 'readonly'
        self.total_cost_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.4', x='0', y='0')

        self.submit_btn = ttk.Button(self.inv_input_lbf, command=self.submit_entry)
        self.submit_btn.configure(text='Submit Entry')
        self.submit_btn.place(anchor='n', relheight='0.1', relwidth='0.5', relx='0.5', rely='0.55', x='0', y='0')

        self.download_btn = ttk.Button(self.inv_input_lbf, command=self.download_inv_data)
        self.download_btn.configure(text='Download Inventory Data')
        self.download_btn.place(anchor='n', relheight='0.1', relwidth='0.5', relx='0.5', rely='0.7', x='0', y='0')

        self.back_btn = ttk.Button(self, text="Back", width=20, command=lambda: controller.show_frame(StartPage))
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.9', rely='0.95')

    def update_inv_trend(self):

        self.ax.cla()
        self.update_all_data()
        df = pd.read_csv(INV_DB).tail(6)
        df.sort_values("Time", inplace=True)
        df.set_index("Time", inplace=True)
        df.plot(kind='bar', ax=self.ax, grid=True)
        self.ax.tick_params(axis="x", labelrotation=0)
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Count of Tyres")
        self.ax.set_title("Tyre Inventory Trend as of {}".format(datetime.now().replace(microsecond=0)))
        self.fig.canvas.draw()

        df = df.tail(1)
        ct = 0
        for c in df.columns:
            ct += 1
            tyre_name_lbl = ttk.Label(self.cur_inv_lbf)
            tyre_name_lbl.configure(font='{source sans pro} 12 {bold}', justify='right', text='{}: '.format(c))
            tyre_name_lbl.place(anchor='ne', relx='0.4', rely='0.{}'.format(ct*18), x='0', y='0')

            tyre_qty_lbl = ttk.Label(self.cur_inv_lbf)
            tyre_qty_lbl.configure(font='{source sans pro} 12 {}', justify='right', text='{} Qty'.format(df[c].values[0]))
            tyre_qty_lbl.place(anchor='nw', relx='0.4', rely='0.{}'.format(ct*18), x='0', y='0')

    def update_all_data(self):
        inv = pd.read_csv(INV_IN_DB, parse_dates=['Datetime'])
        trk = pd.read_csv(TRACK_DB, parse_dates=['Date'])

        inv['Date'] = pd.to_datetime(inv['Datetime'].dt.date)

        df = pd.DataFrame(trk.pivot_table(values='Tyre_Size', index='Date', columns='Tyre_Name', aggfunc='count').to_records())
        df.set_index('Date', inplace=True)
        df = df * -1
        df.reset_index(inplace=True)
        df = df.append(pd.DataFrame(inv.pivot_table(values='Quantity', index='Date', columns='Tyre_Name', aggfunc='sum', fill_value=0).to_records()))

        df.sort_values(['Date'], inplace=True)
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Month'] = df['Month'].apply(lambda x: "0{}".format(x) if x<10 else str(x))
        df['Time'] = df['Year'].astype("str") + "-" + df['Month'].astype("str")

        df.drop(['Date','Year','Month'], inplace=True, axis=1)

        pv = df.pivot_table(values=inv['Tyre_Name'].unique(), index=df['Time'], aggfunc='sum')
        pv = pv.cumsum()
        pv.to_csv(os.path.join(os.getcwd(),"Data","tyre_inventory_db.csv"))

    def submit_entry(self):
        #validate entry:
        if any([self.tyre_name_entry.get() == self._tyre_name_text_, self.qty_entry.get() == self.qty_text_, self.cost_entry.get() == self.cost_text_]):
            pass
        else:
            if tkMessageBox.askyesno("Confirmation", "You've entered the following:\nProduct Name: {}\nProduct Quantiy: {}\nCost\\Unit: {}{}\nTotal Cost: {}{}\nConfirm?".format(self.tyre_name_entry.get(), self.qty_entry.get(), self.currency, self.cost_entry.get(), self.currency, self.total_cost_entry.get())):
                logger.info("User Confirmed")

                ddict = {}
                ddict['Datetime'] = datetime.now().replace(microsecond=0)
                ddict['Tyre_Name'] = self.tyre_name_entry.get()
                ddict['Quantity'] = float(self.qty_entry.get())
                ddict['Cost/Unit'] = float(self.cost_entry.get())
                ddict['Total_Cost'] = float(self.total_cost_entry.get())
                logger.info("Data Extracted - {}".format(ddict))

                df = pd.read_csv(INV_IN_DB, parse_dates=['Datetime'])
                df.sort_values("Datetime", inplace=True)
                df = df.append(pd.DataFrame([ddict]))
                df.to_csv(INV_IN_DB, index=False)
                logger.info("Inventory DB updated")

                self.update_inv_trend()

                tkMessageBox.showinfo("Information", "Update Inventory Success!")

                self.clear_entries(self.tyre_name_entry, self._tyre_name_text_)
                self.clear_entries(self.qty_entry, self.qty_text_)
                self.clear_entries(self.cost_entry, self.cost_text_)
                self.clear_total_cost_entry(self.total_cost_entry, self.total_cost_text_)

            else:
                pass

    def download_inv_data(self):
        exp_dir = tkFileDialog.askdirectory()
        try:
            shutil.copy(INV_IN_DB, os.path.join(exp_dir, INV_IN_FILE_NAME))
        except IOError as io:
            logger.exception("Error copying {} - {}".format(INV_IN_DB, e))

        try:
            shutil.copy(INV_DB, os.path.join(exp_dir, INV_FILE_NAME))
        except IOError as io:
            logger.exception("Error copying {} - {}".format(INV_DB, e))

        if all([os.path.isfile(os.path.join(exp_dir, INV_IN_FILE_NAME)), os.path.isfile(os.path.join(exp_dir, INV_FILE_NAME))]):
            tkMessageBox.showinfo("Success", "File export Success")
        else:
            err_msg = "File export error! - Path: {} is {}, Path {} is {}".format(os.path.join(exp_dir, INV_IN_FILE_NAME), os.path.isfile(os.path.join(exp_dir, INV_IN_FILE_NAME)), os.path.join(exp_dir, INV_FILE_NAME), os.path.isfile(os.path.join(exp_dir, INV_FILE_NAME)))
            logger.error(err_msg)
            tkMessageBox.showerror("Error", err_msg)

    def clear_entries(self, entry_box, entry_text):
        entry_box.delete(0, "end")
        entry_box.insert(0, entry_text)
        entry_box.config(foreground = 'grey')

    def clear_total_cost_entry(self, entry_box, entry_text):
        entry_box['state'] = 'enabled'
        entry_box.delete(0, "end")
        entry_box.insert(0, entry_text)
        entry_box.config(foreground = 'grey')
        entry_box['state'] = 'readonly'

    def on_tyre_name_entry_click(self, event):
        """function that gets called whenever entry is clicked"""
        if self.tyre_name_entry.get() == self._tyre_name_text_:
           self.tyre_name_entry.delete(0, "end")
           self.tyre_name_entry.insert(0, '')
           self.tyre_name_entry.config(foreground = 'black')

    def on_tyre_name_entry_focus_out(self, event):
        """function that checked the entry field after every input"""
        if self.tyre_name_entry.get() == '':
            self.tyre_name_entry.insert(0, self._tyre_name_text_)
            self.tyre_name_entry.config(foreground = 'grey')

    def on_qty_entry_click(self, event):
        """function that gets called whenever entry is clicked"""
        if self.qty_entry.get() == self.qty_text_:
            self.qty_entry.delete(0, "end")
            self.qty_entry.insert(0, '')
            self.qty_entry.config(foreground = 'black')

    def on_qty_entry_focus_out(self, event):
        """function that checked the entry field after every input"""
        if self.qty_entry.get() == '':
            self.qty_entry.insert(0, self.qty_text_)
            self.qty_entry.config(foreground = 'grey')
            self.update_total_cost_entry(self.total_cost_text_)

        elif self.cost_entry.get() != self.cost_text_:
            self.calculate_total_cost()

    def on_cost_entry_click(self, event):
        """function that gets called whenever entry is clicked"""
        if self.cost_entry.get() == self.cost_text_:
            self.cost_entry.delete(0, "end")
            self.cost_entry.insert(0, '')
            self.cost_entry.config(foreground = 'black')

    def on_cost_entry_focus_out(self, event):
        """function that checked the entry field after every input"""
        if self.cost_entry.get() == '':
            self.cost_entry.insert(0, self.cost_text_)
            self.cost_entry.config(foreground = 'grey')
            self.update_total_cost_entry(self.total_cost_text_)

        elif self.qty_entry.get() != self.qty_text_:
            self.calculate_total_cost()

    def update_total_cost_entry(self, total_cost_txt):
        self.total_cost_entry['state'] = 'enabled'
        self.total_cost_entry.delete(0, "end")
        self.total_cost_entry.insert(0, total_cost_txt)
        self.total_cost_entry.config(foreground = 'black')
        self.total_cost_entry['state'] = 'readonly'

    def calculate_total_cost(self):
        try:
            total_cost = round(float(self.qty_entry.get()) * float(self.cost_entry.get()),2)
            total_cost_txt = str(total_cost)
        except Exception as e:
            total_cost_txt = "Error - {}".format(e)
            logger.exception("Error on calculating total cost - {}".format(e))

        self.update_total_cost_entry(total_cost_txt)


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

        self.ctrl_panel = ttk.Labelframe(self)
        self.ctrl_panel.configure(height='200', text='Control Panel', width='200')
        self.ctrl_panel.place(anchor='n', relheight='0.15', relwidth='0.98', relx='0.5', rely='0.06', x='0', y='0')

        self.func_lblf = ttk.Labelframe(self.ctrl_panel)
        self.func_lblf.configure(height='200', text='Select Function', width='200')
        self.func_lblf.place(anchor='nw', relheight='0.9', relwidth='0.15', relx='0.01', rely='0.0', x='0', y='0')

        self._func_tkvar = tk.StringVar(value='Tyre Usage')
        __values = ["Average Tyre Mileage", "Average Vehicle Mileage"]
        self._func_tkvar.trace("w", self.update_setting_menu)
        self.func_menu = tk.OptionMenu(self.func_lblf, self._func_tkvar, 'Tyre Usage', *__values, command=None)
        self.func_menu.place(anchor='nw', relheight='0.98', relwidth='0.98', relx='0.01', rely='0.01', x='0', y='0')

        self.option_lblf = ttk.Labelframe(self.ctrl_panel)
        self.option_lblf.configure(height='200', text='Visualization Settings', width='200')
        self.option_lblf.place(anchor='nw', relheight='0.9', relwidth='0.81', relx='0.18', rely='0.0', x='0', y='0')

        # Plot dummy Canvas
        fig, ax = plt.subplots(tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        plot_widget.place(anchor='n', relheight='0.68', relwidth='0.98', relx='0.5', rely='0.22')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.98', relx='0.5', rely='0.89')

        self.back_btn = ttk.Button(self, text="Back", width=20, command=lambda: controller.show_frame(StartPage))
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.9', rely='0.95')

    def update_setting_menu(self, *args):
        for widget in self.option_lblf.winfo_children():
            widget.destroy()

        if self._func_tkvar.get() == "Tyre Usage":
            self.plot_btn = ttk.Button(self.option_lblf, command=self.track_inv_tyre_usage)
            self.plot_btn.configure(cursor='hand2', text='Plot Chart', width='20')
            self.plot_btn.place(anchor='nw', relheight='0.9', relwidth='0.2', relx='0.01', rely='0.01', x='0', y='0')

        elif self._func_tkvar.get() == "Average Tyre Mileage":
            self._vehnum_tkvar = tk.StringVar(value='Select Vehicle Number')
            _vehnum_values = pd.read_csv(TRACK_DB)['Vehicle_Number'].unique()
            self.sel_veh_num_menu = tk.OptionMenu(self.option_lblf, self._vehnum_tkvar, 'Select Vehicle Number', *_vehnum_values, command=None)
            self.sel_veh_num_menu.place(anchor='nw', relheight='0.8', relwidth='0.2', relx='0.01', rely='0.1', x='0', y='0')

            self._vehtype_tkvar = tk.StringVar(value='Select Vehicle Type')
            _vehtype_values = pd.read_csv(TRACK_DB)['Vehicle_Type'].unique()
            self.sel_veh_type_menu = tk.OptionMenu(self.option_lblf, self._vehtype_tkvar, 'Select Vehicle Type', *_vehtype_values, command=None)
            self.sel_veh_type_menu.place(anchor='nw', relheight='0.8', relwidth='0.2', relx='0.22', rely='0.1', x='0', y='0')

            self.plot_btn = ttk.Button(self.option_lblf, command=self.plot_tyre_mileage)
            self.plot_btn.configure(text='Plot Chart')
            self.plot_btn.place(anchor='nw', relheight='0.8', relwidth='0.2', relx='0.44', rely='0.1', x='0', y='0')

        elif self._func_tkvar.get() == "Average Vehicle Mileage":
            self._vehtype_tkvar = tk.StringVar(value='Select Vehicle Type')
            _vehtype_values = pd.read_csv(TRACK_DB)['Vehicle_Type'].unique()
            self.sel_veh_type_menu = tk.OptionMenu(self.option_lblf, self._vehtype_tkvar, 'Select Vehicle Type', *_vehtype_values, command=None)
            self.sel_veh_type_menu.place(anchor='nw', relheight='0.8', relwidth='0.2', relx='0.01', rely='0.1', x='0', y='0')

            self.plot_btn = ttk.Button(self.option_lblf, command=self.plot_vehicle_mileage)
            self.plot_btn.configure(text='Plot Chart')
            self.plot_btn.place(anchor='nw', relheight='0.8', relwidth='0.2', relx='0.22', rely='0.1', x='0', y='0')

        else:

            pass

    def plot_tyre_mileage(self):
        self.track_tyre_mileage_per_vehicle_type(self._vehnum_tkvar.get(), self._vehtype_tkvar.get())

    def plot_vehicle_mileage(self):
        self.track_per_vehicle_mileage(self._vehtype_tkvar.get())

    def track_tyre_mileage_per_vehicle_type(self, vehicle_number, vehicle_type):
        '''Track per vehicle tyre replacement mileage'''
        df = pd.read_csv(TRACK_DB, parse_dates=['Date'])

        pv = df[(df['Vehicle_Number'] == vehicle_number) & (df['Vehicle_Type'] == vehicle_type)].pivot_table(values="Vehicle_Mileage", index='Date', columns=['Tyre_Location'], aggfunc='mean')

        fig, ax = plt.subplots(tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        plot_widget.place(anchor='n', relheight='0.68', relwidth='0.98', relx='0.5', rely='0.22')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.98', relx='0.5', rely='0.89')

        pv.diff().plot(ax=ax, grid=True,  title="Mileage Per Tyre for - {}".format(vehicle_number), marker='o')
        ax.legend(loc="best", ncol=6)

        # Create custom ticks using matplotlib date tick locator and formatter
        major_loc = mdates.MonthLocator(interval=6)
        minor_loc = mdates.MonthLocator(interval=3)
        ax.xaxis.set_major_locator(major_loc)
        ax.xaxis.set_minor_locator(minor_loc)
        fmt = mdates.DateFormatter('%b\n%Y')
        ax.xaxis.set_major_formatter(fmt)
        ax.grid('on', which='minor', axis='x')
        ax.grid('on', which='major', axis='both')
        ax.tick_params(axis="x", labelrotation=0)

        fig.canvas.draw()

    def track_inv_tyre_usage(self):
        trk = pd.read_csv(TRACK_DB, parse_dates=['Date'])
        inv = pd.read_csv(INV_IN_DB, parse_dates=['Datetime'])

        trk['Date'] = trk['Date'].dt.floor(freq='d')
        inv['Date'] = inv['Datetime'].dt.floor(freq='d')

        df = inv[['Date','Tyre_Name','Quantity']]
        df['Type'] = "IN"
        df['Abs_Qty'] = df['Quantity']

        trk_pv = pd.DataFrame(trk.pivot_table(values='Tyre_Serial', index=['Date','Tyre_Name'], aggfunc='count').to_records())
        trk_pv['Quantity'] = trk_pv['Tyre_Serial']
        trk_pv.drop("Tyre_Serial", axis=1, inplace=True)
        trk_pv['Type'] = "OUT"
        trk_pv['Abs_Qty'] = trk_pv['Quantity'] * -1

        df = df.append(trk_pv)
        df.sort_values("Date", inplace=True)
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Month'] = df['Month'].apply(lambda x: calendar.month_abbr[x])

        pv = df.pivot_table(values='Quantity', index=['Date'], columns=["Type"], aggfunc='sum', fill_value=0)

        cum_pv = df.pivot_table(values='Abs_Qty', index=['Date'], columns=["Tyre_Name"], aggfunc='sum', fill_value=0).cumsum()

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        plot_widget.place(anchor='n', relheight='0.68', relwidth='0.98', relx='0.5', rely='0.22')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.98', relx='0.5', rely='0.89')

        pv.plot(title="Tyre Inventory IN/OUT Quantity", ax = ax1, marker='o')
        cum_pv.plot(title="Tyre usage trend", ax = ax2, marker='o', color=["r", "k", "c", "m"])

        for ax in [ax1, ax2]:
            ax.legend(loc='best')
            ax.grid('on', which='major', axis='both')
            ax.tick_params(axis="x", labelrotation=0)

        fig.canvas.draw()

    def track_per_vehicle_mileage(self, vehicle_type):
        '''Track per vehicle tyre replacement mileage'''
        df = pd.read_csv(TRACK_DB, parse_dates=['Date'])

        pv = df[df['Vehicle_Type'] == vehicle_type].pivot_table(values="Vehicle_Mileage", index='Vehicle_Number', columns=['Tyre_Location'], aggfunc='mean')

        fig, ax = plt.subplots(tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        plot_widget.place(anchor='n', relheight='0.68', relwidth='0.98', relx='0.5', rely='0.22')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.98', relx='0.5', rely='0.89')

        pv.plot(ax=ax, title="Average Mileage Per {}".format(vehicle_type), marker='o')
        ax.legend(loc="best", ncol=6)

        ax.grid('on', which='major', axis='both' )
        ax.tick_params(axis="x", labelrotation=0)

        fig.canvas.draw()


# ----- Execution ----- #


if __name__ == "__main__":

    # Create logger
    logger = create_logger(__name__, __file__, __version__, 10)

    # Launch App
    app = TyreApp()
    app.mainloop()
