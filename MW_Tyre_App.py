#!/usr/bin/env python3
#-----------------------------------------------------------------------------#
#                                                                             #
#                            Python script                                    #
#                                                                             #
#-----------------------------------------------------------------------------#
#
# Ident        : MY_Tyre_App.py
__version__ = "1.0.0-alpha"
__author__ = "Adrian Loo"
"""
The Tyre App for tracking tyre usage and inventory for Modern Wong
"""
#
# History
# 2021-09-29: 0.0.1 [Adrian Loo] Development start
# 2021-09-29: 0.0.1 [Adrian Loo] Complete StartPage
# 2021-09-30: 0.0.1 [Adrian Loo] Fix page size and position
# 2021-10-01: 0.0.1 [Adrian Loo] Complete Track Inventory Page
# 2021-10-02: 0.0.1 [Adrian Loo] Complete Track Inventory Page functions
# 2021-10-04: 0.0.1 [Adrian Loo] Complete Dashboard Page, functions and visualization
# 2021-10-04: 0.0.1 [Adrian Loo] Complete Tyre Tracking page, functions and visuals
# 2021-10-05: 0.0.1 [Adrian Loo] Complete Tyre Tracking page, check Serial Number function
# 2021-10-06: 0.0.1 [Adrian Loo] Fix exit issue by adding sys.exit() created exe version release. Fix Plot issue when data set in empty. Add entry clear function after tyre data submission.
# 2021-10-13: 1.0.0-alpha [Adrian Loo] Complete Track Tyre Page functions and display, StartPage GUI Design and ConfigPage setup
# 2021-10-15: 1.0.0-alpha [Adrian Loo] Complete ConfigPage UI design
# 2021-10-17: 1.0.0-alpha [Adrian Loo] Add create_config(), clear_vehicle_profile() and update_vehicle()
# 2021-10-18: 1.0.0-alpha [Adrian Loo] Add focus in/out for config page entries, update profile methods.
# 2021-10-19: 1.0.0-alpha [Adrian Loo] Complete ConfigPage functions
# 2021-10-20: 1.0.0-alpha [Adrian Loo] Complete Tyre Tracking and Inventory Page functions
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
import matplotlib.backends.backend_tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

import numpy as np
import pandas as pd

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox
from tkinter import simpledialog as tkSimpleDialog

from xml.etree import ElementTree as ET
from xml.dom import minidom

import warnings
warnings.filterwarnings("ignore")

# ----- Methods ----- #

LARGE_FONT = ("Verdana", 12, "bold")
LB_FONT = ("Verdana", 11, "bold")
RB_FONT = ("Verdana", 10)

CONFIG_SOURCE = os.path.join(os.getcwd(), "Config")
CONFIG_FILE = os.path.join(CONFIG_SOURCE, "systemconfig.xml")

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

    file_handler = logging.FileHandler(os.path.join(log_dir, f'{os.path.basename(basefile).split(".")[0]}_{str(datetime.now().date())}.log'))
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
        self.resizable(False, False)  # Change to not resizable to manage image rendering and tk.entry positioning
        self.minsize(1016, 600)

        style = ttk.Style(self)
        logger.info("Themes available - {}".format(style.theme_names()))
        logger.info("Theme in use - {}".format(style.theme_use()))
        style.configure("TRadiobutton", font=RB_FONT)
        style.configure("TLabelframe.Label", foreground='black', font=LB_FONT)

        logger.info("Application initialized")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, TrackInvPage, TrackTyrePage, DashboardPage, ConfigPage):

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Validate if configuration has entries
        if os.path.isfile(CONFIG_FILE):
            if self.check_config_profiles():
                logger.info("Loading Start page")
                self.start_frame(StartPage)
            else:
                logger.info("Loading Configuration page")
                self.start_frame(ConfigPage)
        else:
            logger.info("No Configuration file found, creating default configuration file")
            self.create_config()
            logger.info("Loading Configuration page")
            tkMessageBox.showinfo("Information", "Welcome to ModernWong Transport Tyre Tracking App.\n\n\nTo start using the app, please fill in the profiles for the following:\n\n\n1. Vehicles - enter your fleet numbers\n\n2. Tyre - Enter the information for the tyres you have in stock\n\n3. Employee - Enter the employee names who will be in charge or replacing tyres")
            self.start_frame(ConfigPage)

        self.protocol('WM_DELETE_WINDOW', self.on_exit)

    def check_config_profiles(self):
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()

        profiles = []
        for i in root:
            if i.tag != "App":
                prof_entries = len(i.findall(f"{i.tag}Profile"))
                logger.info(f"{i.tag}Profile has {prof_entries} entries")
                if prof_entries >= 1:
                    profiles.append(1)
                else:
                    profiles.append(0)
            else:
                pass

        if all(profiles):
            logger.info("All profiles have entries")
            return True
        else:
            logger.info("Some Profile(s) have no entry")
            return False

    def create_config(self):
        '''create defaut configuration file'''
        root = minidom.Document()

        system = root.createElement('System')
        root.appendChild(system)

        elements = ['App','Vehicle','Tyre','Employee']

        for element in elements:
            elementChild = root.createElement(element)
            if element == "App":
                subElement = root.createElement("AppSettings")
                subElement.setAttribute("Currency", "RM")
                elementChild.appendChild(subElement)
            system.appendChild(elementChild)

        xml_str = root.toprettyxml(indent ="\t")
        with open(CONFIG_FILE, "w") as f:
            f.write(xml_str)

    def load_profile_list(self, profile, key):
        '''Loads up the config file (xml), search for the profile and key to return a list of values'''
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()

        values = []
        el_ls = root.findall(profile)[0].findall(f"{profile}Profile")
        for el in el_ls:
            values.append(el.attrib[key])

        return values

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
            sys.exit()
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
        self.track_tyre_lbl.place(anchor='n', relx='0.5', rely='0.3')

        self.track_inv_lbl = ttk.Label(self)
        self.track_inv_lbl.configure(
            font='{source sans pro} 18 {bold}', justify='center', text='Track\nInventory')
        self.track_inv_lbl.place(anchor='n', relx='0.3', rely='0.3')

        self.dashboard_lbl = ttk.Label(self)
        self.dashboard_lbl.configure(
            font='{source sans pro} 18 {bold}', justify='center', text='Launch\nDashboard')
        self.dashboard_lbl.place(anchor='n', relx='0.7', rely='0.3')

        self.track_tyre_btn = ttk.Button(
            self, command=lambda: controller.show_frame(TrackTyrePage))
        self.mw_blue_truck_png = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "Config", 'wheel.png'))
        self.track_tyre_btn.configure(
            image=self.mw_blue_truck_png, text='Track Tyre')
        self.track_tyre_btn.place(
            anchor='n', height='140', width='140', relx='0.5', rely='0.435')

        self.track_inv_btn = ttk.Button(
            self, command=lambda: controller.show_frame(TrackInvPage))
        self.mw_green_truck_png = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "Config", 'inventory.png'))
        self.track_inv_btn.configure(
            image=self.mw_green_truck_png, text='Track Inventory')
        self.track_inv_btn.place(
            anchor='n', height='140', width='140', relx='0.3', rely='0.435')

        self.launch_db_btn = ttk.Button(
            self, command=lambda: controller.show_frame(DashboardPage))
        self.mw_white_truck_png = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "Config", 'dashboard.png'))
        self.launch_db_btn.configure(
            image=self.mw_white_truck_png, text='Launch Dashboard')
        self.launch_db_btn.place(
            anchor='n', height='140', width='140', relx='0.7', rely='0.435')

        self.settings_btn = ttk.Button(
            self, command=lambda: controller.show_frame(ConfigPage))
        self.settings_png = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "Config", 'settings.png'))
        self.settings_btn.configure(
            image=self.settings_png, text='Launch Settings')
        self.settings_btn.place(
            anchor='n', height='75', width='75', relx='0.9', rely='0.82')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.5', rely='0.9')


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
        self.total_cost_lbl.place(anchor='ne', relx='0.4', rely='0.435', x='0', y='0')

        self.add_tyre_btn = ttk.Button(self.inv_input_lbf, command=lambda: controller.show_frame(ConfigPage))
        self.add_tyre_btn.configure(text='Add New Tyre')
        self.add_tyre_btn.place(anchor='ne', relx='0.98', rely='0.01', x='0', y='0')

        self.tyrenm_tkvar = tk.StringVar(value='Select Tyre Name')
        self.tyrenm_values = controller.load_profile_list("Tyre", "Tyre_name")
        self.tyrenm_opt = tk.OptionMenu(self.inv_input_lbf, self.tyrenm_tkvar, 'Select Tyre Name', *self.tyrenm_values, command=None)
        self.tyrenm_opt.configure(font='{source sans pro} 14 {}')
        self.tyrenm_opt.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.1', x='0', y='0')

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
        self.total_cost_entry.place(anchor='nw', relheight='0.06', relwidth='0.5', relx='0.4', rely='0.435', x='0', y='0')

        self.submit_btn = ttk.Button(self.inv_input_lbf, command=self.submit_entry)
        self.submit_btn.configure(text='Submit Entry')
        self.submit_btn.place(anchor='n', relheight='0.1', relwidth='0.5', relx='0.5', rely='0.55', x='0', y='0')

        self.download_btn = ttk.Button(self.inv_input_lbf, command=self.download_inv_data)
        self.download_btn.configure(text='Download Inventory Data')
        self.download_btn.place(anchor='n', relheight='0.1', relwidth='0.5', relx='0.5', rely='0.7', x='0', y='0')

        self.back_btn = ttk.Button(self, text="Back to Main", width=20, command=lambda: controller.show_frame(StartPage))
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.tyre_btn = ttk.Button(self, text="Track Tyre", width=20, command=lambda: controller.show_frame(TrackTyrePage))
        self.tyre_btn.place(anchor='n', relx='0.37', rely='0.95')

        self.dash_btn = ttk.Button(self, text="Dashboard", width=20, command=lambda: controller.show_frame(DashboardPage))
        self.dash_btn.place(anchor='n', relx='0.64', rely='0.95')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.9', rely='0.95')

    def update_inv_trend(self):
        try:
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
        except Exception as e:
            logger.exception(f"Error Updating inventory - {e}")
            self.fig.canvas.draw()

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
        if any([self.tyrenm_tkvar.get() == "Select Tyre Name", self.qty_entry.get() == self.qty_text_, self.cost_entry.get() == self.cost_text_]):
            tkMessageBox.showerror("Error", "Some missing information.\nPlease check entry and try again.")
        else:
            if tkMessageBox.askyesno("Confirmation", "You've entered the following:\nProduct Name: {}\nProduct Quantiy: {}\nCost\\Unit: {}{}\nTotal Cost: {}{}\nConfirm?".format(self.tyrenm_tkvar.get(), self.qty_entry.get(), self.currency, self.cost_entry.get(), self.currency, self.total_cost_entry.get())):
                logger.info("User Confirmed")

                ddict = {}
                ddict['Datetime'] = datetime.now().replace(microsecond=0)
                ddict['Tyre_Name'] = self.tyrenm_tkvar.get()
                ddict['Quantity'] = float(self.qty_entry.get())
                ddict['Cost/Unit'] = float(self.cost_entry.get())
                ddict['Total_Cost'] = float(self.total_cost_entry.get())
                logger.info("Data Extracted - {}".format(ddict))

                try:
                    df = pd.read_csv(INV_IN_DB, parse_dates=['Datetime'])
                    df.sort_values("Datetime", inplace=True)
                    df = df.append(pd.DataFrame([ddict]))
                    df.to_csv(INV_IN_DB, index=False)
                    logger.info("Inventory DB updated")
                except:
                    df = pd.DataFrame([ddict])
                    df.to_csv(INV_IN_DB, index=False)
                    logger.info("Inventory DB updated")


                self.update_inv_trend()

                tkMessageBox.showinfo("Information", "Update Inventory Success!")

                self.tyrenm_tkvar.set("Select Tyre Name")
                self.clear_entries(self.qty_entry, self.qty_text_)
                self.clear_entries(self.cost_entry, self.cost_text_)
                self.clear_total_cost_entry(self.total_cost_entry, self.total_cost_text_)

            else:
                pass

    def download_inv_data(self):
        exp_dir = tkFileDialog.askdirectory()

        if os.path.isdir(exp_dir):
            logger.info(f"Export directory - [{exp_dir}]")
            try:
                shutil.copy(INV_IN_DB, os.path.join(exp_dir, INV_IN_FILE_NAME))
            except IOError as io:
                logger.exception(f"Error copying {INV_IN_DB} - {e}")

            try:
                shutil.copy(INV_DB, os.path.join(exp_dir, INV_FILE_NAME))
            except IOError as io:
                logger.exception(f"Error copying {INV_DB} - {e}")

            if all([os.path.isfile(os.path.join(exp_dir, INV_IN_FILE_NAME)), os.path.isfile(os.path.join(exp_dir, INV_FILE_NAME))]):
                tkMessageBox.showinfo("Success", "File export Success")
            else:
                path1 = os.path.join(exp_dir, INV_IN_FILE_NAME)
                path1_st = os.path.isfile(path1)
                path2 = os.path.join(exp_dir, INV_FILE_NAME)
                path2_st = os.path.isfile(path2)
                err_msg = f"File export error! - Path: {path1} is {path1_st}, Path {path2} is {path2_st}"
                logger.error(err_msg)
                tkMessageBox.showerror("Error", err_msg)
        else:
            logger.error(f"Directory not selected, download operation skipped - {exp_dir}")

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
            logger.exception(f"Error on calculating total cost - {e}")

        self.update_total_cost_entry(total_cost_txt)


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

        # --- Start View Labelframe --- #
        self.view_lbf = ttk.Labelframe(self)

        self.view_vehnum_tkvar = tk.StringVar(value='Select Vehicle Number')
        self.view_vehnum_values = controller.load_profile_list("Vehicle", "Truck_num")
        self.view_vehnum_opt = tk.OptionMenu(self.view_lbf, self.view_vehnum_tkvar, 'Select Vehicle Number', *self.view_vehnum_values, command=None)
        self.view_vehnum_opt.place(anchor='ne', relheight='0.5', relwidth='0.5', relx='0.52', rely='0.02', x='0', y='0')

        self.view_clr_btn = ttk.Button(self.view_lbf, command=self.clear_tyre_data)
        self.view_clr_btn.configure(text='Clear Display')
        self.view_clr_btn.place(anchor='ne', relwidth='0.5', relx='0.52', rely='0.6', x='0', y='0')

        self.view_chk_btn = ttk.Button(self.view_lbf, command=self.check_tyre_data)
        self.view_chk_btn.configure(text='Display Record')
        self.view_chk_btn.place(anchor='nw', relheight='0.5', relwidth='0.42', relx='0.55', rely='0.02', x='0', y='0')

        self.view_dl_btn = ttk.Button(self.view_lbf, command=self.download_tyre_data)
        self.view_dl_btn.configure(text='Download Record')
        self.view_dl_btn.place(anchor='nw', relwidth='0.42', relx='0.55', rely='0.6', x='0', y='0')

        self.view_lbf.configure(height='200', text='View Tyres', width='200')
        self.view_lbf.place(anchor='n', relheight='0.15', relwidth='0.28', relx='0.15', rely='0.06', x='0', y='0')
        # --- End View Labelframe --- #

        # --- Start Update Labelframe --- #
        self.update_lbf = ttk.Labelframe(self)

        self.update_date_lbl = ttk.Label(self.update_lbf)
        self.update_date_lbl.configure(font='{source sans pro} 11 {}', text='Date: ')
        self.update_date_lbl.place(anchor='ne', relx='0.08', rely='0.01', x='0', y='0')

        self.update_act_lbl = ttk.Label(self.update_lbf)
        self.update_act_lbl.configure(font='{source sans pro} 11 {}', text='Activity: ')
        self.update_act_lbl.place(anchor='ne', relx='0.08', rely='0.31', x='0', y='0')

        self.update_reason_lbl = ttk.Label(self.update_lbf)
        self.update_reason_lbl.configure(font='{source sans pro} 11 {}', text='Reason: ')
        self.update_reason_lbl.place(anchor='ne', relx='0.08', rely='0.61', x='0', y='0')

        self.update_clr_btn = ttk.Button(self.update_lbf, command=self.clear_vehicle_tyre_data)
        self.update_clr_btn.configure(text='Clear Entry')
        self.update_clr_btn.place(anchor='ne', relheight='0.55', relwidth='0.1', relx='0.76', rely='0.31', x='0', y='0')

        self.date_entry = ttk.Entry(self.update_lbf)
        self.date_entry.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.date_ent_txt = '''Eg: 2021-10-22'''
        self.date_entry.delete('0', 'end')
        self.date_entry.insert('0', self.date_ent_txt)
        self.date_entry.bind('<FocusIn>', self.on_widget_click)
        self.date_entry.place(anchor='nw', relwidth='0.18', relx='0.08', x='0', y='0')

        self.activity_tkvar = tk.StringVar(value='Select Activity')
        self.activity_values = ['Tyre Replacement', 'Wheel Replacement']
        self.activity_opt = tk.OptionMenu(self.update_lbf, self.activity_tkvar, 'Select Activity', *self.activity_values, command=None)
        self.activity_opt.place(anchor='nw', relheight='0.3', relwidth='0.18', relx='0.08', rely='0.28', x='0', y='0')

        self.reason_entry = ttk.Entry(self.update_lbf)
        self.reason_entry.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.reason_ent_txt = '''Eg: Tyre Worn Out'''
        self.reason_entry.delete('0', 'end')
        self.reason_entry.insert('0', self.reason_ent_txt)
        self.reason_entry.bind('<FocusIn>', self.on_widget_click)
        self.reason_entry.place(anchor='nw', relwidth='0.18', relx='0.08', rely='0.61', x='0', y='0')

        self.update_emp_lbl = ttk.Label(self.update_lbf)
        self.update_emp_lbl.configure(font='{source sans pro} 11 {}', text='Employee Name: ')
        self.update_emp_lbl.place(anchor='ne', relx='0.42', x='0', y='0')

        self.update_vehnum_lbl = ttk.Label(self.update_lbf)
        self.update_vehnum_lbl.configure(font='{source sans pro} 11 {}', text='Vehicle Number: ')
        self.update_vehnum_lbl.place(anchor='ne', relx='0.42', rely='0.31', x='0', y='0')

        self.update_mile_lbl = ttk.Label(self.update_lbf)
        self.update_mile_lbl.configure(font='{source sans pro} 11 {}', text='Vehicle Mileage: ')
        self.update_mile_lbl.place(anchor='ne', relx='0.42', rely='0.61', x='0', y='0')

        self.emp_tkvar = tk.StringVar(value='Select Employee')
        self.emp_values = controller.load_profile_list("Employee", "Emp_name")
        self.empname_opt = tk.OptionMenu(self.update_lbf, self.emp_tkvar, 'Select Employee', *self.emp_values, command=None)
        self.empname_opt.place(anchor='nw', relheight='0.3', relwidth='0.18', relx='0.42', rely='-0.02', x='0', y='0')

        self.vehnum_tkvar = tk.StringVar(value='Select Vehicle')
        self.vehnum_values = controller.load_profile_list("Vehicle", "Truck_num")
        self.vehnum_opt = tk.OptionMenu(self.update_lbf, self.vehnum_tkvar, 'Select Vehicle', *self.vehnum_values, command=None)
        self.vehnum_opt.place(anchor='nw', relheight='0.3', relwidth='0.18', relx='0.42', rely='0.28', x='0', y='0')

        self.mile_entry = ttk.Entry(self.update_lbf)
        self.mile_entry.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.mile_ent_txt = '''Eg: 23456'''
        self.mile_entry.delete('0', 'end')
        self.mile_entry.insert('0', self.mile_ent_txt)
        self.mile_entry.bind('<FocusIn>', self.on_widget_click)
        self.mile_entry.place(anchor='nw', relwidth='0.18', relx='0.42', rely='0.61', x='0', y='0')

        self.tyrename_lbl = ttk.Label(self.update_lbf)
        self.tyrename_lbl.configure(font='{source sans pro} 11 {}', text='Tyre Name: ')
        self.tyrename_lbl.place(anchor='ne', relx='0.76', x='0', y='0')

        self.tyrename_tkvar = tk.StringVar(value='Select Tyre Name')
        self.tyrename_values = controller.load_profile_list("Tyre", "Tyre_name")
        self.tyrename_opt = tk.OptionMenu(self.update_lbf, self.tyrename_tkvar, 'Select Tyre Name', *self.tyrename_values, command=None)
        self.tyrename_opt.place(anchor='nw', relheight='0.3', relwidth='0.18', relx='0.76', rely='-0.02', x='0', y='0')

        self.update_submit_btn = ttk.Button(self.update_lbf)
        self.update_submit_btn.configure(text='Submit Entry')
        self.update_submit_btn.place(anchor='nw', relheight='0.55', relwidth='0.17', relx='0.765', rely='0.31', x='0', y='0')

        self.update_lbf.configure(height='200', text='Update Tyres', width='200')
        self.update_lbf.place(anchor='n', relheight='0.15', relwidth='0.69', relx='0.64', rely='0.06', x='0', y='0')
        # --- End Update Labelframe --- #

        # --- Start Display Labelframe --- #
        self.display_lbf = ttk.Labelframe(self)
        self.display_lbf.configure(height='200', labelanchor='n', text='Display Frame', width='200')
        self.display_lbf.place(anchor='n', relheight='0.7', relwidth='0.98', relx='0.5', rely='0.22', x='0', y='0')

        #loc_img = Image.open(os.path.join(os.getcwd(), "Config", "tyre_location.png"))
        self.tyreloc_lbl = ttk.Label(self.display_lbf)
        self.tyre_locations_png = tk.PhotoImage(file=os.path.join(os.getcwd(), "Config", "tyre_locations.png"))
        self.tyreloc_lbl.configure(image=self.tyre_locations_png, text='tyre location')
        self.tyreloc_lbl.pack(side='top')

        self.side_view_lbl = ttk.Label(self.display_lbf)
        self.side_view_lbl.configure(font='{source sans pro} 11 {bold}', text='Side View')
        self.side_view_lbl.place(anchor='n', relx='0.5', rely='0.28', x='0', y='0')

        self.bottom_view_lbl = ttk.Label(self.display_lbf)
        self.bottom_view_lbl.configure(font='{source sans pro} 11 {bold}', text='Bottom View')
        self.bottom_view_lbl.place(anchor='n', relx='0.5', rely='0.93', x='0', y='0')

        self.tyre_ent_text_ = '''Enter S/N'''

        self.s1_l_ent = ttk.Entry(self.display_lbf)
        self.s1_l_ent.configure(foreground='grey', justify='center')
        self.s1_l_ent.delete('0', 'end')
        self.s1_l_ent.insert('0', self.tyre_ent_text_)
        self.s1_l_ent.bind('<FocusIn>', self.on_widget_click)
        self.s1_l_ent.place(anchor='n', relwidth='0.065', relx='0.095', rely='0.435', x='0', y='0')

        self.s1_r_ent = ttk.Entry(self.display_lbf)
        self.s1_r_ent.configure(foreground='grey', justify='center')
        self.s1_r_ent.delete('0', 'end')
        self.s1_r_ent.insert('0', self.tyre_ent_text_)
        self.s1_r_ent.bind('<FocusIn>', self.on_widget_click)
        self.s1_r_ent.place(anchor='n', relwidth='0.065', relx='0.095', rely='0.851', x='0', y='0')

        self.d1_l_out_ent = ttk.Entry(self.display_lbf)
        self.d1_l_out_ent.configure(foreground='grey', justify='center')
        self.d1_l_out_ent.delete('0', 'end')
        self.d1_l_out_ent.insert('0', self.tyre_ent_text_)
        self.d1_l_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.d1_l_out_ent.place(anchor='n', relwidth='0.065', relx='0.3', rely='0.435', x='0', y='0')

        self.d1_l_in_ent = ttk.Entry(self.display_lbf)
        self.d1_l_in_ent.configure(foreground='grey', justify='center')
        self.d1_l_in_ent.delete('0', 'end')
        self.d1_l_in_ent.insert('0', self.tyre_ent_text_)
        self.d1_l_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.d1_l_in_ent.place(anchor='n', relwidth='0.065', relx='0.3', rely='0.495', x='0', y='0')

        self.d1_r_in_ent = ttk.Entry(self.display_lbf)
        self.d1_r_in_ent.configure(foreground='grey', justify='center')
        self.d1_r_in_ent.delete('0', 'end')
        self.d1_r_in_ent.insert('0', self.tyre_ent_text_)
        self.d1_r_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.d1_r_in_ent.place(anchor='n', relwidth='0.065', relx='0.3', rely='0.791', x='0', y='0')

        self.d1_r_out_ent = ttk.Entry(self.display_lbf)
        self.d1_r_out_ent.configure(foreground='grey', justify='center')
        self.d1_r_out_ent.delete('0', 'end')
        self.d1_r_out_ent.insert('0', self.tyre_ent_text_)
        self.d1_r_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.d1_r_out_ent.place(anchor='n', relwidth='0.065', relx='0.3', rely='0.851', x='0', y='0')

        self.d2_l_out_ent = ttk.Entry(self.display_lbf)
        self.d2_l_out_ent.configure(foreground='grey', justify='center')
        self.d2_l_out_ent.delete('0', 'end')
        self.d2_l_out_ent.insert('0', self.tyre_ent_text_)
        self.d2_l_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.d2_l_out_ent.place(anchor='n', relwidth='0.065', relx='0.38', rely='0.435', x='0', y='0')

        self.d2_l_in_ent = ttk.Entry(self.display_lbf)
        self.d2_l_in_ent.configure(foreground='grey', justify='center')
        self.d2_l_in_ent.delete('0', 'end')
        self.d2_l_in_ent.insert('0', self.tyre_ent_text_)
        self.d2_l_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.d2_l_in_ent.place(anchor='n', relwidth='0.065', relx='0.38', rely='0.495', x='0', y='0')

        self.d2_r_in_ent = ttk.Entry(self.display_lbf)
        self.d2_r_in_ent.configure(foreground='grey', justify='center')
        self.d2_r_in_ent.delete('0', 'end')
        self.d2_r_in_ent.insert('0', self.tyre_ent_text_)
        self.d2_r_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.d2_r_in_ent.place(anchor='n', relwidth='0.065', relx='0.38', rely='0.791', x='0', y='0')

        self.d2_r_out_ent = ttk.Entry(self.display_lbf)
        self.d2_r_out_ent.configure(foreground='grey', justify='center')
        self.d2_r_out_ent.delete('0', 'end')
        self.d2_r_out_ent.insert('0', self.tyre_ent_text_)
        self.d2_r_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.d2_r_out_ent.place(anchor='n', relwidth='0.065', relx='0.38', rely='0.851', x='0', y='0')

        self.ta1_l_out_ent = ttk.Entry(self.display_lbf)
        self.ta1_l_out_ent.configure(foreground='grey', justify='center')
        self.ta1_l_out_ent.delete('0', 'end')
        self.ta1_l_out_ent.insert('0', self.tyre_ent_text_)
        self.ta1_l_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta1_l_out_ent.place(anchor='n', relwidth='0.065', relx='.669', rely='0.435', x='0', y='0')

        self.ta1_l_in_ent = ttk.Entry(self.display_lbf)
        self.ta1_l_in_ent.configure(foreground='grey', justify='center')
        self.ta1_l_in_ent.delete('0', 'end')
        self.ta1_l_in_ent.insert('0', self.tyre_ent_text_)
        self.ta1_l_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta1_l_in_ent.place(anchor='n', relwidth='0.065', relx='.669', rely='0.495', x='0', y='0')

        self.ta1_r_in_ent = ttk.Entry(self.display_lbf)
        self.ta1_r_in_ent.configure(foreground='grey', justify='center')
        self.ta1_r_in_ent.delete('0', 'end')
        self.ta1_r_in_ent.insert('0', self.tyre_ent_text_)
        self.ta1_r_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta1_r_in_ent.place(anchor='n', relwidth='0.065', relx='.669', rely='0.791', x='0', y='0')

        self.ta1_r_out_ent = ttk.Entry(self.display_lbf)
        self.ta1_r_out_ent.configure(foreground='grey', justify='center')
        self.ta1_r_out_ent.delete('0', 'end')
        self.ta1_r_out_ent.insert('0', self.tyre_ent_text_)
        self.ta1_r_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta1_r_out_ent.place(anchor='n', relwidth='0.065', relx='.669', rely='0.851', x='0', y='0')

        self.ta2_l_out_ent = ttk.Entry(self.display_lbf)
        self.ta2_l_out_ent.configure(foreground='grey', justify='center')
        self.ta2_l_out_ent.delete('0', 'end')
        self.ta2_l_out_ent.insert('0', self.tyre_ent_text_)
        self.ta2_l_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta2_l_out_ent.place(anchor='n', relwidth='0.065', relx='.741', rely='0.435', x='0', y='0')

        self.ta2_l_in_ent = ttk.Entry(self.display_lbf)
        self.ta2_l_in_ent.configure(foreground='grey', justify='center')
        self.ta2_l_in_ent.delete('0', 'end')
        self.ta2_l_in_ent.insert('0', self.tyre_ent_text_)
        self.ta2_l_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta2_l_in_ent.place(anchor='n', relwidth='0.065', relx='.741', rely='0.495', x='0', y='0')

        self.ta2_r_in_ent = ttk.Entry(self.display_lbf)
        self.ta2_r_in_ent.configure(foreground='grey', justify='center')
        self.ta2_r_in_ent.delete('0', 'end')
        self.ta2_r_in_ent.insert('0', self.tyre_ent_text_)
        self.ta2_r_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta2_r_in_ent.place(anchor='n', relwidth='0.065', relx='.741', rely='0.791', x='0', y='0')

        self.ta2_r_out_ent = ttk.Entry(self.display_lbf)
        self.ta2_r_out_ent.configure(foreground='grey', justify='center')
        self.ta2_r_out_ent.delete('0', 'end')
        self.ta2_r_out_ent.insert('0', self.tyre_ent_text_)
        self.ta2_r_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta2_r_out_ent.place(anchor='n', relwidth='0.065', relx='.741', rely='0.851', x='0', y='0')

        self.ta3_l_out_ent = ttk.Entry(self.display_lbf)
        self.ta3_l_out_ent.configure(foreground='grey', justify='center')
        self.ta3_l_out_ent.delete('0', 'end')
        self.ta3_l_out_ent.insert('0', self.tyre_ent_text_)
        self.ta3_l_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta3_l_out_ent.place(anchor='n', relwidth='0.065', relx='.813', rely='0.435', x='0', y='0')

        self.ta3_l_in_ent = ttk.Entry(self.display_lbf)
        self.ta3_l_in_ent.configure(foreground='grey', justify='center')
        self.ta3_l_in_ent.delete('0', 'end')
        self.ta3_l_in_ent.insert('0', self.tyre_ent_text_)
        self.ta3_l_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta3_l_in_ent.place(anchor='n', relwidth='0.065', relx='.813', rely='0.495', x='0', y='0')

        self.ta3_r_in_ent = ttk.Entry(self.display_lbf)
        self.ta3_r_in_ent.configure(foreground='grey', justify='center')
        self.ta3_r_in_ent.delete('0', 'end')
        self.ta3_r_in_ent.insert('0', self.tyre_ent_text_)
        self.ta3_r_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta3_r_in_ent.place(anchor='n', relwidth='0.065', relx='.813', rely='0.791', x='0', y='0')

        self.ta3_r_out_ent = ttk.Entry(self.display_lbf)
        self.ta3_r_out_ent.configure(foreground='grey', justify='center')
        self.ta3_r_out_ent.delete('0', 'end')
        self.ta3_r_out_ent.insert('0', self.tyre_ent_text_)
        self.ta3_r_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta3_r_out_ent.place(anchor='n', relwidth='0.065', relx='.813', rely='0.851', x='0', y='0')

        self.ta4_l_out_ent = ttk.Entry(self.display_lbf)
        self.ta4_l_out_ent.configure(foreground='grey', justify='center')
        self.ta4_l_out_ent.delete('0', 'end')
        self.ta4_l_out_ent.insert('0', self.tyre_ent_text_)
        self.ta4_l_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta4_l_out_ent.place(anchor='n', relwidth='0.065', relx='0.885', rely='0.435', x='0', y='0')

        self.ta4_l_in_ent = ttk.Entry(self.display_lbf)
        self.ta4_l_in_ent.configure(foreground='grey', justify='center')
        self.ta4_l_in_ent.delete('0', 'end')
        self.ta4_l_in_ent.insert('0', self.tyre_ent_text_)
        self.ta4_l_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta4_l_in_ent.place(anchor='n', relwidth='0.065', relx='0.885', rely='0.495', x='0', y='0')

        self.ta4_r_in_ent = ttk.Entry(self.display_lbf)
        self.ta4_r_in_ent.configure(foreground='grey', justify='center')
        self.ta4_r_in_ent.delete('0', 'end')
        self.ta4_r_in_ent.insert('0', self.tyre_ent_text_)
        self.ta4_r_in_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta4_r_in_ent.place(anchor='n', relwidth='0.065', relx='0.885', rely='0.791', x='0', y='0')

        self.ta4_r_out_ent = ttk.Entry(self.display_lbf)
        self.ta4_r_out_ent.configure(foreground='grey', justify='center')
        self.ta4_r_out_ent.delete('0', 'end')
        self.ta4_r_out_ent.insert('0', self.tyre_ent_text_)
        self.ta4_r_out_ent.bind('<FocusIn>', self.on_widget_click)
        self.ta4_r_out_ent.place(anchor='n', relwidth='0.065', relx='0.885', rely='0.851', x='0', y='0')

        self.back_btn = ttk.Button(self, text="Back to Main", width=20, command=lambda: controller.show_frame(StartPage))
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.inv_btn = ttk.Button(self, text="Track Inventory", width=20, command=lambda: controller.show_frame(TrackInvPage))
        self.inv_btn.place(anchor='n', relx='0.37', rely='0.95')

        self.dash_btn = ttk.Button(self, text="Dashboard", width=20, command=lambda: controller.show_frame(DashboardPage))
        self.dash_btn.place(anchor='n', relx='0.64', rely='0.95')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.9', rely='0.95')

        ent_ls = [self.s1_l_ent, self.s1_r_ent, self.d1_l_in_ent, self.d1_l_out_ent, self.d2_l_in_ent, self.d2_l_out_ent, self.d1_r_in_ent, self.d1_r_out_ent, self.d2_r_in_ent, self.d2_r_out_ent, self.ta1_l_in_ent, self.ta1_l_out_ent, self.ta2_l_in_ent, self.ta2_l_out_ent, self.ta3_l_in_ent, self.ta3_l_out_ent, self.ta4_l_in_ent, self.ta4_l_out_ent, self.ta1_r_in_ent, self.ta1_r_out_ent, self.ta2_r_in_ent, self.ta2_r_out_ent, self.ta3_r_in_ent, self.ta3_r_out_ent, self.ta4_r_in_ent, self.ta4_r_out_ent]

        var_ls = ['s1_l', 's1_r', 'd1_l_in', 'd1_l_out', 'd2_l_in', 'd2_l_out', 'd1_r_in', 'd1_r_out', 'd2_r_in', 'd2_r_out', 'ta1_l_in', 'ta1_l_out', 'ta2_l_in', 'ta2_l_out', 'ta3_l_in', 'ta3_l_out', 'ta4_l_in', 'ta4_l_out', 'ta1_r_in', 'ta1_r_out', 'ta2_r_in', 'ta2_r_out', 'ta3_r_in', 'ta3_r_out', 'ta4_r_in', 'ta4_r_out']

        self.ent_dict = {}
        for i in var_ls:
            self.ent_dict[i] = ent_ls[var_ls.index(i)]

        self.widget_entry = {}

        self.default_entries = {self.date_entry: self.date_ent_txt, self.reason_entry: self.reason_ent_txt, self.mile_entry: self.mile_ent_txt}

        self.default_options = [self.activity_tkvar, self.emp_tkvar, self.vehnum_tkvar, self.tyrename_tkvar]
        self.default_options_values = ["Select Activity", "Select Employee", "Select Vehicle", "Select Tyre Name"]

        self.page_clear = True

    def submit_tyre_data(self):

        if tkMessageBox.askyesno("Confirm?", "Are you sure you want to save data?\nYou cannot undo this action."):
            pass
        else:
            return

        # Validate Parameters Entry
        validate_ls = [self.date_entry.get() == self.date_ent_txt, self.activity_tkvar.get() == "Select Activity", self.reason_entry.get() == self.reason_ent_txt, self.emp_tkvar.get() == "Select Employee", self.vehnum_tkvar.get() == "Select Vehicle", self.mile_entry.get() == self.mile_ent_txt, self.tyrename_tkvar.get() == "Select Tyre Name"]

        try:
            evt_date = pd.to_datetime(self.date_entry.get())
            logger.info(f"Event Date is valid - {evt_date}")
        except Exception as e:
            logger.exception(f"Error when checking time - {e}")
            tkMessageBox.showerror("Error", "Date input error, please check again")
            return

        try:
            evt_mile = int(self.mile_entry.get())
            logger.info(f"Event Mileage is valid - {evt_mile}")
        except Exception as e:
            logger.exception(f"Error when checking mileage - {e}")
            tkMessageBox.showerror("Error", "Mileage input error, please check again")
            return

        dlist = []
        if any(validate_ls):
            tkMessageBox.showwarning("Warning", "Some Fields not entered")
            return
        else:
            logger.info(f"All Entry is valid - {validate_ls}")
            for k, v in self.ent_dict.items():
                if v.get() == self.tyre_ent_text_:
                    pass
                else:
                    try:
                        ddict = {}
                        ddict['Date'] = evt_date
                        ddict['Activity'] = self.activity_tkvar.get()
                        ddict['Reason'] = self.reason_entry.get()
                        ddict['Employee_Name'] = self.emp_tkvar.get()
                        ddict['Tyre_Name'] = self.tyrename_tkvar.get()
                        ddict['Tyre_Serial'] = v.get()
                        ddict['Vehicle_Number'] = self.vehnum_tkvar.get()
                        ddict['Vehicle_Type'] = "Trailer" if k[0] == "t" else "Truck"
                        ddict['Vehicle_Mileage'] = evt_mile
                        ddict['Tyre_Location'] = k.upper().replace("_","-")
                        ddict['Tyre_Size'] = "295/80R22.5"
                        dlist.append(ddict)
                        logger.info(f"Appended - {ddict}")
                    except Exception as e:
                        logger.exception(f"Error appending input - {e}")
                        tkMessageBox.showerror("Error", "Error appending input. Please contact developer.")

            df = pd.read_csv(TRACK_DB, parse_dates=['Date'])
            df = df.append(pd.DataFrame(dlist))

            df.to_csv(TRACK_DB, index=False)

            tkMessageBox.showinfo("Success", "Tyre Event Updated")

            self.clear_vehicle_tyre_data()

    def check_tyre_data(self):
        if self.view_vehnum_tkvar.get() == "Select Vehicle Number":
            tkMessageBox.showerror("Error", "Please select a vehicle number to display record")
            return None
        else:
            pass

        try:
            df = pd.read_csv(TRACK_DB, parse_dates=['Date'])
            df = df[df['Vehicle_Number'] == self.view_vehnum_tkvar.get()]
            df.reset_index(drop=True, inplace=True)

            self.view_veh_lbl = ttk.Label(self.display_lbf)
            self.view_veh_lbl.configure(background="#4D6073", foreground='white', font='{Source Sans Pro} 11 {bold} {underline}',
                                      justify='center', text='Vehicle Information')
            self.view_veh_lbl.place(anchor='n', relx='0.52', rely='0.58')

            mileage = df[df['Date'] == df['Date'].max()]['Vehicle_Mileage'].max()
            last_mod = df['Date'].max().date()

            self.view_veh_info_lbl = ttk.Label(self.display_lbf)
            self.view_veh_info_lbl.configure(background="#4D6073", foreground='white', font='{Source Sans Pro} 11 {}', justify='center', text=f"Vehicle Number: {self.view_vehnum_tkvar.get()}\nVehicle Mileage: {mileage}km\nLast Modified: {last_mod}")
            self.view_veh_info_lbl.place(anchor='n', relx='0.52', rely='0.63')

            for loc in df['Tyre_Location'].unique():
                sdf = df[df['Tyre_Location'] == loc]
                sdf = sdf[sdf['Date'] == sdf['Date'].max()]
                serial = sdf['Tyre_Serial'].values[0]
                ent_field = self.ent_dict[loc.lower().replace("-","_")]
                ent_field.delete(0, "end")
                ent_field.insert(0, serial)
                ent_field.config(foreground = "blue")

            self.page_clear = False

        except Exception as e:
            tkMessageBox.showerror("Error", "Please check Vehicle Number selection")
            self.clear_tyre_data()

    def clear_vehicle_tyre_data(self):
        self.clear_vehicle_data()
        self.clear_tyre_data()

    def clear_vehicle_data(self):
        try:
            for ent, txt in self.default_entries.items():
                ent.delete(0, "end")
                ent.insert(0, txt)
                ent.config(foreground = "grey")
        except Exception as e:
            logger.exception(f"Error clearing vehicle entries - {ent}, {txt} - {e}")

        try:
            for i in range(0, len(self.default_options)):
                self.default_options[i].set(self.default_options_values[i])
        except Exception as e:
            logger.exception(f"Error clearing options - {opt}, {var} - {e}")

    def clear_tyre_data(self):
        try:
            self.view_veh_lbl.destroy()
            self.view_veh_info_lbl.destroy()
        except Exception as e:
            logger.exception(f"Error destroying view labels - {e}")

        for key, ent_field in self.ent_dict.items():
            ent_field.delete(0, "end")
            ent_field.insert(0, self.tyre_ent_text_)
            ent_field.config(foreground = "grey")

    def download_tyre_data(self):
        exp_dir = tkFileDialog.askdirectory()

        if os.path.isdir(exp_dir):
            logger.info(f"Export directory - [{exp_dir}]")
            try:
                shutil.copy(TRACK_DB, os.path.join(exp_dir, TRACK_FILE_NAME))
            except IOError as io:
                logger.exception(f"Error copying {TRACK_DB} - {e}")

            if all([os.path.isfile(os.path.join(exp_dir, TRACK_FILE_NAME)), os.path.isfile(os.path.join(exp_dir, TRACK_FILE_NAME))]):
                tkMessageBox.showinfo("Success", "File export Success")
            else:
                err_msg = "File export error! - Path: {} is {}".format(os.path.join(exp_dir, TRACK_FILE_NAME), os.path.isfile(os.path.join(exp_dir, TRACK_FILE_NAME)))
                logger.error(err_msg)
                tkMessageBox.showerror("Error", err_msg)
        else:
            logger.error(f"Directory not selected, download operation skipped - {exp_dir}")

    def on_widget_click(self, evt):
        self.widget = self.focus_get()
        logger.info(f"{self.widget} is in focus")
        if self.page_clear:
            if self.widget in self.widget_entry.keys():
                self.widget_data = self.widget_entry[self.widget]
                if self.widget.get() == self.widget_entry[self.widget]:
                    self.clear_entry_field()
                else:
                    logger.info(f"Widget [{self.widget}] has user data - {self.widget.get()}")
            else:
                logger.info(f"Widget [{self.widget}] has no user data.")
                self.widget_data = self.widget.get()
                self.widget_entry[self.widget] = self.widget_data
                self.clear_entry_field()
        else:
            self.update_clr_btn.focus_set()
            if tkMessageBox.askyesno("Attention", "The display port has data.\nWould you like to clear it?"):
                self.clear_tyre_data()
                self.page_clear = True
                self.widget.focus_set()
            else:
                tkMessageBox.showwarning("Warning", "You need to clear the display port before entering new data")

    def clear_entry_field(self):
        logger.info("Clearing Entry Field for user input")
        self.widget.delete(0, "end")
        self.widget.insert(0, '')
        self.widget.config(foreground = 'black')
        self.widget.bind('<FocusOut>', self.on_widget_focusout)

    def on_widget_focusout(self, evt):
        if self.widget.get() == '':
            logger.info("Widget [{}] is empty - Returning original placeholder".format(self.widget))
            self.widget.insert(0, self.widget_data)
            self.widget.config(foreground = 'grey')


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

        self.plot_btn = ttk.Button(self.option_lblf, command=self.track_inv_tyre_usage)
        self.plot_btn.configure(cursor='hand2', text='Plot Chart', width='20')
        self.plot_btn.place(anchor='nw', relheight='0.9', relwidth='0.2', relx='0.01', rely='0.01', x='0', y='0')

        # Plot dummy Canvas
        fig, ax = plt.subplots(tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        plot_widget.place(anchor='n', relheight='0.68', relwidth='0.98', relx='0.5', rely='0.22')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.98', relx='0.5', rely='0.851')
        self.track_inv_tyre_usage()

        self.back_btn = ttk.Button(self, text="Back to Main", width=20, command=lambda: controller.show_frame(StartPage))
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.inv_btn = ttk.Button(self, text="Track Inventory", width=20, command=lambda: controller.show_frame(TrackInvPage))
        self.inv_btn.place(anchor='n', relx='0.37', rely='0.95')

        self.tyre_btn = ttk.Button(self, text="Track Tyre", width=20, command=lambda: controller.show_frame(TrackTyrePage))
        self.tyre_btn.place(anchor='n', relx='0.64', rely='0.95')

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

        fig, ax = plt.subplots(tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        plot_widget.place(anchor='n', relheight='0.68', relwidth='0.98', relx='0.5', rely='0.22')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.98', relx='0.5', rely='0.851')

        try:
            df = pd.read_csv(TRACK_DB, parse_dates=['Date'])

            pv = df[(df['Vehicle_Number'] == vehicle_number) & (df['Vehicle_Type'] == vehicle_type)].pivot_table(values="Vehicle_Mileage", index='Date', columns=['Tyre_Location'], aggfunc='mean')

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

        except Exception as e:
            logger.exception(f"Error drawing tyre inventory usage - {e}")

        fig.canvas.draw()

    def track_inv_tyre_usage(self):

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        plot_widget.place(anchor='n', relheight='0.68', relwidth='0.98', relx='0.5', rely='0.22')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.98', relx='0.5', rely='0.851')

        try:
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

            pv.plot(title="Tyre Inventory IN/OUT Quantity", ax = ax1, marker='o')
            cum_pv.plot(title="Tyre usage trend", ax = ax2, marker='o', color=["r", "k", "c", "m"])

            for ax in [ax1, ax2]:
                ax.legend(loc='best')
                ax.grid('on', which='major', axis='both')
                ax.tick_params(axis="x", labelrotation=0)
        except Exception as e:
            logger.exception(f"Error drawing tyre inventory usage - {e}")

        fig.canvas.draw()

    def track_per_vehicle_mileage(self, vehicle_type):
        '''Track per vehicle tyre replacement mileage'''

        fig, ax = plt.subplots(tight_layout=True)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plot_widget = canvas.get_tk_widget()
        plot_widget.place(anchor='n', relheight='0.68', relwidth='0.98', relx='0.5', rely='0.22')
        plt.rcParams.update({'font.size': 7})
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.config(background='white')
        toolbar.update()
        toolbar.place(anchor='n', relheight='0.05', relwidth='0.98', relx='0.5', rely='0.851')

        try:
            df = pd.read_csv(TRACK_DB, parse_dates=['Date'])

            pv = df[df['Vehicle_Type'] == vehicle_type].pivot_table(values="Vehicle_Mileage", index='Vehicle_Number', columns=['Tyre_Location'], aggfunc='mean')

            pv.plot(ax=ax, title="Average Mileage Per {}".format(vehicle_type), marker='o')
            ax.legend(loc="best", ncol=6)

            ax.grid('on', which='major', axis='both' )
            ax.tick_params(axis="x", labelrotation=0)

        except Exception as e:
            logger.exception(f"Error drawing tyre inventory usage - {e}")

        fig.canvas.draw()


class ConfigPage(tk.Frame):
    '''
    The configuration page of the app
    '''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(height=str(controller.winfo_height()-20), width=str(controller.winfo_width()-20))
        self.grid(column='0', row='0', sticky='n')

        self.header_lbl = ttk.Label(self)
        self.header_lbl.configure(font='{Source Sans Pro} 20 {bold}',
                                  justify='center', text='Configuration')
        self.header_lbl.place(anchor='n', relx='0.5', rely='0.01')

        # --- Vehicle Profile Section --- #
        self.veh_profile_lbf = ttk.Labelframe(self)
        self.veh_profile_lbf.configure(height='200', text='Vehicle Profile', width='200')
        self.veh_profile_lbf.place(anchor='n', relheight='0.2', relwidth='0.41', relx='0.215', rely='0.06', x='0', y='0')

        self.cfg_truck_num_lbl = ttk.Label(self.veh_profile_lbf)
        self.cfg_truck_num_lbl.configure(font='{source sans pro} 11 {bold}', text='Truck Number: ')
        self.cfg_truck_num_lbl.place(anchor='ne', relx='0.3', rely='0.05', x='0', y='0')

        self.cfg_truck_num_ent = ttk.Entry(self.veh_profile_lbf)
        self.cfg_truck_num_ent.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.cfg_truck_num_text = '''Eg: JAB2866T'''
        self.cfg_truck_num_ent.delete('0', 'end')
        self.cfg_truck_num_ent.insert('0', self.cfg_truck_num_text)
        self.cfg_truck_num_ent.bind('<FocusIn>', self.on_widget_click)
        self.cfg_truck_num_ent.place(anchor='nw', relx='0.3', rely='0.05', x='0', y='0')

        self.cfg_trailer_num_lbl = ttk.Label(self.veh_profile_lbf)
        self.cfg_trailer_num_lbl.configure(font='{source sans pro} 11 {bold}', text='Trailer Number: ')
        self.cfg_trailer_num_lbl.place(anchor='ne', relx='0.3', rely='0.35', x='0', y='0')

        self.cfg_trailer_num_ent = ttk.Entry(self.veh_profile_lbf)
        self.cfg_trailer_num_ent.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.cfg_trailer_num_text = '''Eg: JAB2866T'''
        self.cfg_trailer_num_ent.delete('0', 'end')
        self.cfg_trailer_num_ent.insert('0', self.cfg_trailer_num_text)
        self.cfg_trailer_num_ent.bind('<FocusIn>', self.on_widget_click)
        self.cfg_trailer_num_ent.place(anchor='nw', relx='0.3', rely='0.35', x='0', y='0')

        self.cfg_veh_submit_btn = ttk.Button(self.veh_profile_lbf, command=self.update_vehicle)
        self.cfg_veh_submit_btn.configure(text='Submit Vehicle Profile')
        self.cfg_veh_submit_btn.place(anchor='n', relx='0.5', rely='0.65', x='0', y='0')

        self.cfg_veh_load_btn = ttk.Button(self.veh_profile_lbf, command=self.load_vehicle_data)
        self.cfg_veh_load_btn.configure(text='Load & Edit\nVehicle Data')
        self.cfg_veh_load_btn.place(anchor='ne', relheight='0.8', relwidth='0.2', relx='0.95', rely='0.05', x='0', y='0')

        # --- Tyre Profile Section --- #
        self.tyre_profile_lbf = ttk.Labelframe(self)
        self.tyre_profile_lbf.configure(height='200', text='Tyre Profile', width='200')
        self.tyre_profile_lbf.place(anchor='n', relheight='0.5', relwidth='0.2', relx='0.11', rely='0.27', x='0', y='0')

        self.cfg_tyre_brand_lbl = ttk.Label(self.tyre_profile_lbf)
        self.cfg_tyre_brand_lbl.configure(font='{source sans pro} 11 {bold}', text='Brand: ')
        self.cfg_tyre_brand_lbl.place(anchor='ne', relx='0.35', rely='0.05', x='0', y='0')

        self.cfg_tyre_brand_ent = ttk.Entry(self.tyre_profile_lbf)
        self.cfg_tyre_brand_ent.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.cfg_tyre_brand_text = '''Eg: Austone'''
        self.cfg_tyre_brand_ent.delete('0', 'end')
        self.cfg_tyre_brand_ent.insert('0', self.cfg_tyre_brand_text)
        self.cfg_tyre_brand_ent.bind('<FocusIn>', self.on_widget_click)
        self.cfg_tyre_brand_ent.place(anchor='nw', relwidth='0.55', relx='0.35', rely='0.05', x='0', y='0')

        self.cfg_tyre_name_lbl = ttk.Label(self.tyre_profile_lbf)
        self.cfg_tyre_name_lbl.configure(font='{source sans pro} 11 {bold}', text='Product: ')
        self.cfg_tyre_name_lbl.place(anchor='ne', relx='0.35', rely='0.15', x='0', y='0')

        self.cfg_tyre_name_ent = ttk.Entry(self.tyre_profile_lbf)
        self.cfg_tyre_name_ent.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.cfg_tyre_name_text = '''Eg: AT1023'''
        self.cfg_tyre_name_ent.delete('0', 'end')
        self.cfg_tyre_name_ent.insert('0', self.cfg_tyre_name_text)
        self.cfg_tyre_name_ent.bind('<FocusIn>', self.on_widget_click)
        self.cfg_tyre_name_ent.place(anchor='nw', relwidth='0.55', relx='0.35', rely='0.15', x='0', y='0')

        self.cfg_tyre_size_lbl = ttk.Label(self.tyre_profile_lbf)
        self.cfg_tyre_size_lbl.configure(font='{source sans pro} 11 {bold}', text='Size: ')
        self.cfg_tyre_size_lbl.place(anchor='ne', relx='0.35', rely='0.25', x='0', y='0')

        self.cfg_tyre_size_ent = ttk.Entry(self.tyre_profile_lbf)
        self.cfg_tyre_size_ent.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.cfg_tyre_size_text = '''Eg: 295/80R22.5'''
        self.cfg_tyre_size_ent.delete('0', 'end')
        self.cfg_tyre_size_ent.insert('0', self.cfg_tyre_size_text)
        self.cfg_tyre_size_ent.bind('<FocusIn>', self.on_widget_click)
        self.cfg_tyre_size_ent.place(anchor='nw', relwidth='0.55', relx='0.35', rely='0.25', x='0', y='0')

        self.cfg_tyre_submit_btn = ttk.Button(self.tyre_profile_lbf, command=self.update_tyre)
        self.cfg_tyre_submit_btn.configure(text='Submit Tyre Profile')
        self.cfg_tyre_submit_btn.place(anchor='n', relx='0.5', rely='0.4', x='0', y='0')

        self.cfg_tyre_load_btn = ttk.Button(self.tyre_profile_lbf, command=self.load_tyre_data)
        self.cfg_tyre_load_btn.configure(text='Load & Edit\nTyre Data')
        self.cfg_tyre_load_btn.place(anchor='n', relheight='0.2', relwidth='0.5', relx='0.5', rely='0.7', x='0', y='0')

        # --- Employee profile section --- #
        self.emp_profile_lbf = ttk.Labelframe(self)
        self.emp_profile_lbf.configure(height='200', text='Employee Profile', width='200')
        self.emp_profile_lbf.place(anchor='n', relheight='0.5', relwidth='0.2', relx='0.32', rely='0.27', x='0', y='0')

        self.cfg_emp_name_lbl = ttk.Label(self.emp_profile_lbf)
        self.cfg_emp_name_lbl.configure(font='{source sans pro} 11 {bold}', text='Name: ')
        self.cfg_emp_name_lbl.place(anchor='ne', relx='0.35', rely='0.05', x='0', y='0')

        self.cfg_emp_name_ent = ttk.Entry(self.emp_profile_lbf)
        self.cfg_emp_name_ent.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.cfg_emp_name_text = '''Eg: Sudin'''
        self.cfg_emp_name_ent.delete('0', 'end')
        self.cfg_emp_name_ent.insert('0', self.cfg_emp_name_text)
        self.cfg_emp_name_ent.bind('<FocusIn>', self.on_widget_click)
        self.cfg_emp_name_ent.place(anchor='nw', relwidth='0.55', relx='0.35', rely='0.05', x='0', y='0')

        self.cfg_emp_contact_lbl = ttk.Label(self.emp_profile_lbf)
        self.cfg_emp_contact_lbl.configure(font='{source sans pro} 11 {bold}', text='Contact: ')
        self.cfg_emp_contact_lbl.place(anchor='ne', relx='0.35', rely='0.15', x='0', y='0')

        self.cfg_emp_contact_ent = ttk.Entry(self.emp_profile_lbf)
        self.cfg_emp_contact_ent.configure(foreground='grey', font='{source sans pro} 11 {}')
        self.cfg_emp_contact_text = '''Eg: +60123456789'''
        self.cfg_emp_contact_ent.delete('0', 'end')
        self.cfg_emp_contact_ent.insert('0', self.cfg_emp_contact_text)
        self.cfg_emp_contact_ent.bind('<FocusIn>', self.on_widget_click)
        self.cfg_emp_contact_ent.place(anchor='nw', relwidth='0.55', relx='0.35', rely='0.15', x='0', y='0')

        self.cfg_emp_submit_btn = ttk.Button(self.emp_profile_lbf, command=self.update_employee)
        self.cfg_emp_submit_btn.configure(text='Submit Employee Profile')
        self.cfg_emp_submit_btn.place(anchor='n', relx='0.5', rely='0.4', x='0', y='0')

        self.cfg_emp_load_btn = ttk.Button(self.emp_profile_lbf, command=self.load_employee_data)
        self.cfg_emp_load_btn.configure(text='Load & Edit\nEmployee Data')
        self.cfg_emp_load_btn.place(anchor='n', relheight='0.2', relwidth='0.5', relx='0.5', rely='0.7', x='0', y='0')

        # --- App Settings Section --- #
        self.app_settings_lbf = ttk.Labelframe(self)
        self.app_settings_lbf.configure(height='200', text='App Settings', width='200')
        self.app_settings_lbf.place(anchor='n', relheight='0.15', relwidth='0.41', relx='0.215', rely='0.775', x='0', y='0')

        self.cfg_currency_lbl = ttk.Label(self.app_settings_lbf)
        self.cfg_currency_lbl.configure(font='{source sans pro} 11 {bold}', text='Currency: ')
        self.cfg_currency_lbl.place(anchor='ne', relx='0.2', rely='0.1', x='0', y='0')

        self.currency_tkvar = tk.StringVar(value='RM')
        self.currency_values = ['SGD']
        self.cfg_currency_opt = tk.OptionMenu(self.app_settings_lbf, self.currency_tkvar, 'RM', *self.currency_values, command=None)
        self.cfg_currency_opt.place(anchor='nw', relwidth='0.15', relx='0.2', rely='0.05', x='0', y='0')

        self.cfg_setting_save_btn = ttk.Button(self.app_settings_lbf, command=self.save_app_settings)
        self.cfg_setting_save_btn.configure(text='Save Settings')
        self.cfg_setting_save_btn.place(anchor='se', relwidth='0.2', relx='0.95', rely='0.8', x='0', y='0')

        # --- Display Port --- #
        self.display_port_lbf = ttk.Labelframe(self)
        self.display_port_lbf.configure(height='200', labelanchor='n', text='Display Port', width='200')
        self.display_port_lbf.place(anchor='n', relheight='0.865', relwidth='0.56', relx='0.71', rely='0.06', x='0', y='0')
        # --- End of Display Port --- #

        self.back_btn = ttk.Button(self, text="Back to Main", width=20, command=self.back_to_main)
        self.back_btn.place(anchor='n', relx='0.1', rely='0.95')

        self.exit_btn = ttk.Button(self, text="Close", width=20, command=lambda: controller.on_exit())
        self.exit_btn.place(anchor='n', relx='0.9', rely='0.95')

        # --- Setting default value references --- #
        self.default_vehicle = {self.cfg_truck_num_ent: self.cfg_truck_num_text, self.cfg_trailer_num_ent: self.cfg_trailer_num_text}

        self.default_tyre= {self.cfg_tyre_brand_ent: self.cfg_tyre_brand_text, self.cfg_tyre_name_ent: self.cfg_tyre_name_text, self.cfg_tyre_size_ent: self.cfg_tyre_size_text}

        self.default_employee = {self.cfg_emp_name_ent: self.cfg_emp_name_text, self.cfg_emp_contact_ent: self.cfg_emp_contact_text}

        self.widget_entry = {}

    def on_widget_click(self, evt):
        self.widget = self.focus_get()
        logger.info(f"{self.widget} is in focus")
        if self.widget in self.widget_entry.keys():
            self.widget_data = self.widget_entry[self.widget]
            if self.widget.get() == self.widget_entry[self.widget]:
                self.clear_entry_field()
            else:
                logger.info(f"Widget [{self.widget}] has user data - {self.widget.get()}")
        else:
            logger.info(f"Widget [{self.widget}] has no user data.")
            self.widget_data = self.widget.get()
            self.widget_entry[self.widget] = self.widget_data
            self.clear_entry_field()

    def clear_entry_field(self):
        logger.info("Clearing Entry Field for user input")
        self.widget.delete(0, "end")
        self.widget.insert(0, '')
        self.widget.config(foreground = 'black')
        self.widget.bind('<FocusOut>', self.on_widget_focusout)

    def on_widget_focusout(self, evt):
        if self.widget.get() == '':
            logger.info("Widget [{}] is empty - Returning original placeholder".format(self.widget))
            self.widget.insert(0, self.widget_data)
            self.widget.config(foreground = 'grey')

    def clear_vehicle_profile_ent(self):
        for wg, txt in self.default_vehicle.items():
            wg.delete(0, "end")
            wg.insert(0, txt)
            wg.config(foreground = "grey")

    def update_vehicle(self):
        '''Updates Vehicle Profile to systemconfig.xml file'''

        validate = []
        for wg, txt in self.default_vehicle.items():
            if wg.get() == txt:
                validate.append(1)
            else:
                validate.append(0)
        if any(validate):
            tkMessageBox.showwarning("Warning", "You need to enter info to submit.\nPlease try again.")
            return None
        else:
            attrib = {"Truck_num": self.cfg_truck_num_ent.get(), "Trailer_num": self.cfg_trailer_num_ent.get()}
            logger.info(f"User input: [{attrib}]")

        if tkMessageBox.askyesno("Confirm?", f"Truck Number: {attrib['Truck_num']}\nTrailer Number: {attrib['Trailer_num']}\nDo you want to proceed?"):
            logger.info("User proceed")

            tree = ET.parse(CONFIG_FILE)
            root = tree.getroot()
            for i in root:
                if i.tag == 'Vehicle':
                    ET.SubElement(i, "VehicleProfile", attrib)
                    dom = minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
                else:
                    pass

            with open(CONFIG_FILE, 'w') as fw:
                fw.writelines(line + "\n" for line in dom.toprettyxml().split("\n") if not line.strip() == "")
            logger.info(f"Data written into configuration - [{attrib}]")
        else:
            logger.info("User aborted")
            pass

        self.clear_vehicle_profile_ent()

    def clear_tyre_profile_ent(self):
        for wg, txt in self.default_tyre.items():
            wg.delete(0, "end")
            wg.insert(0, txt)
            wg.config(foreground = "grey")

    def update_tyre(self):
        '''Updates Tyre Profile to systemconfig.xml file'''

        validate = []
        for wg, txt in self.default_tyre.items():
            if wg.get() == txt:
                validate.append(1)
            else:
                validate.append(0)
        if any(validate):
            tkMessageBox.showwarning("Warning", "You need to enter info to submit.\nPlease try again.")
            return None
        else:
            attrib = {"Tyre_brand": self.cfg_tyre_brand_ent.get(), "Tyre_name": self.cfg_tyre_name_ent.get(), "Tyre_size": self.cfg_tyre_size_ent.get()}
            logger.info(f"User input: [{attrib}]")

        if tkMessageBox.askyesno("Confirm?", f"Tyre Brand: {attrib['Tyre_brand']}\nTyre Name: {attrib['Tyre_name']}\nTyre Size: {attrib['Tyre_size']}\nDo you want to proceed?"):
            logger.info("User proceed")

            tree = ET.parse(CONFIG_FILE)
            root = tree.getroot()
            for i in root:
                if i.tag == 'Tyre':
                    ET.SubElement(i, "TyreProfile", attrib)
                    dom = minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
                else:
                    pass

            with open(CONFIG_FILE, 'w') as fw:
                fw.writelines(line + "\n" for line in dom.toprettyxml().split("\n") if not line.strip() == "")
            logger.info(f"Data written into configuration - [{attrib}]")
        else:
            logger.info("User aborted")
            pass

        self.clear_tyre_profile_ent()

    def clear_employee_profile_ent(self):
        for wg, txt in self.default_employee.items():
            wg.delete(0, "end")
            wg.insert(0, txt)
            wg.config(foreground = "grey")

    def update_employee(self):
        '''Updates Employee Profile to systemconfig.xml file'''

        validate = []
        for wg, txt in self.default_employee.items():
            if wg.get() == txt:
                validate.append(1)
            else:
                validate.append(0)
        if any(validate):
            tkMessageBox.showwarning("Warning", "You need to enter info to submit.\nPlease try again.")
            return None
        else:
            attrib = {"Emp_name": self.cfg_emp_name_ent.get(), "Emp_contact": self.cfg_emp_contact_ent.get()}
            logger.info(f"User input: [{attrib}]")

        if tkMessageBox.askyesno("Confirm?", f"Employee Name: {attrib['Emp_name']}\nEmployee Contact: {attrib['Emp_contact']}\nDo you want to proceed?"):
            logger.info("User proceed")

            tree = ET.parse(CONFIG_FILE)
            root = tree.getroot()
            for i in root:
                if i.tag == 'Employee':
                    ET.SubElement(i, "EmployeeProfile", attrib)
                    dom = minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
                else:
                    pass

            with open(CONFIG_FILE, 'w') as fw:
                fw.writelines(line + "\n" for line in dom.toprettyxml().split("\n") if not line.strip() == "")
            logger.info(f"Data written into configuration - [{attrib}]")
        else:
            logger.info("User aborted")
            pass

        self.clear_employee_profile_ent()

    def save_app_settings(self):
        '''Update app settings to systemconfig.xml file'''
        user_select_text = f"Currency: {self.currency_tkvar.get()}\nDo you want to proceed?"
        if tkMessageBox.askyesno("Confirm?", user_select_text):
            logger.info("User Proceed")

            tree = ET.parse(CONFIG_FILE)
            root = tree.getroot()

            for el in list(root.findall("App")[0].iter()):
                if el.tag == "AppSettings" and "Currency" in el.attrib.keys():
                    el.attrib['Currency'] = self.currency_tkvar.get()
                else:
                    pass

            xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="\t")
            with open(CONFIG_FILE, 'w') as fw:
                fw.writelines(line + "\n" for line in xmlstr.split("\n") if not line.strip() == "")
        else:
            logger.info("User abort")

    def clear_cfg_display_port(self):
        '''clean up display port'''
        try:
            for widget in self.display_port_lbf.winfo_children():
                widget.destroy()
                logger.info(f"Child destroyed - {widget}")
        except Exception as e:
            logger.exception(f"Error destroying children - {widget}")

    def load_vehicle_data(self):
        '''function to populate vehicle data into view port'''

        # Clear viewport first
        self.clear_cfg_display_port()

        # Load Configuration data
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()

        self.head_lblf = ttk.Labelframe(self.display_port_lbf)
        self.head_lblf.configure(text='Vehicle Information', labelanchor='n')
        # head_lblf.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=20)
        self.head_lblf.pack()

        id_lbl = tk.Entry(self.head_lblf,)
        id_lbl.delete('0', 'end')
        id_lbl.insert('0', "ID")
        id_lbl.configure(state='disabled', width=3, justify='center')
        id_lbl.grid(row=0, column=0)

        truck_num_lbl = tk.Entry(self.head_lblf, text='Truck Number')
        truck_num_lbl.delete('0', 'end')
        truck_num_lbl.insert('0', 'Truck Number')
        truck_num_lbl.configure(state='disabled', justify='center')
        truck_num_lbl.grid(row=0, column=1)

        trailer_num_lbl = tk.Entry(self.head_lblf, text='Trailer Number')
        trailer_num_lbl.delete('0', 'end')
        trailer_num_lbl.insert('0', 'Trailer Number')
        trailer_num_lbl.configure(state='disabled', justify='center')
        trailer_num_lbl.grid(row=0, column=2)

        del_lbl = tk.Entry(self.head_lblf, text="Del")
        del_lbl.delete('0', 'end')
        del_lbl.insert('0', "Del")
        del_lbl.configure(state='disabled', width=6, justify='center')
        del_lbl.grid(row=0, column=3)

        ct = 1
        for el in root.findall("Vehicle")[0].findall("VehicleProfile"):

            lblf = ttk.Labelframe(self.display_port_lbf)
            lblf.configure(cursor='hand2')
            # lblf.grid(row=ct, column=0, columnspan=4, sticky='nsew', padx=20)
            lblf.pack()
            lblf.bind('<Enter>', self.check_row)

            id_ent = tk.Entry(lblf)
            id_ent.delete('0', 'end')
            id_ent.insert('0', str(ct))
            id_ent.configure(state='disabled', width=3, justify='center')
            id_ent.grid(row=0, column=0)

            truck_ent = tk.Entry(lblf)
            truck_ent.delete('0', 'end')
            truck_ent.insert('0', el.attrib['Truck_num'])
            truck_ent.configure(state='disabled', justify='center')
            truck_ent.grid(row=0, column=1)

            trailer_ent = tk.Entry(lblf)
            trailer_ent.delete('0', 'end')
            trailer_ent.insert('0', el.attrib['Trailer_num'])
            trailer_ent.configure(state='disabled', justify='center')
            trailer_ent.grid(row=0, column=2)

            del_btn = tk.Button(lblf, text='X', width=4)
            del_btn.configure(state='disabled')
            del_btn.grid(row=0, column=3)
            del_btn.bind('<Button-1>', self.del_row)
            del_btn.bind('<Leave>', self.disable_btn)

            ct += 1

        save_btn = ttk.Button(self.display_port_lbf, text="Save", width=20, command=self.save_display_changes)
        save_btn.pack()

    def load_tyre_data(self):
        '''function to populate tyre data into view port'''

        # Clear viewport first
        self.clear_cfg_display_port()

        # Load Configuration data
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()

        self.head_lblf = ttk.Labelframe(self.display_port_lbf)
        self.head_lblf.configure(text='Tyre Information', labelanchor='n')
        # head_lblf.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=20)
        self.head_lblf.pack()

        id_lbl = tk.Entry(self.head_lblf,)
        id_lbl.delete('0', 'end')
        id_lbl.insert('0', "ID")
        id_lbl.configure(state='disabled', width=3, justify='center')
        id_lbl.grid(row=0, column=0)

        tyre_brand_lbl = tk.Entry(self.head_lblf, text='Tyre Brand')
        tyre_brand_lbl.delete('0', 'end')
        tyre_brand_lbl.insert('0', 'Tyre Brand')
        tyre_brand_lbl.configure(state='disabled', justify='center')
        tyre_brand_lbl.grid(row=0, column=1)

        tyre_name_lbl = tk.Entry(self.head_lblf, text='Tyre Name')
        tyre_name_lbl.delete('0', 'end')
        tyre_name_lbl.insert('0', 'Tyre Name')
        tyre_name_lbl.configure(state='disabled', justify='center')
        tyre_name_lbl.grid(row=0, column=2)

        tyre_size_lbl = tk.Entry(self.head_lblf, text='Tyre Size')
        tyre_size_lbl.delete('0', 'end')
        tyre_size_lbl.insert('0', 'Tyre Size')
        tyre_size_lbl.configure(state='disabled', justify='center')
        tyre_size_lbl.grid(row=0, column=3)

        del_lbl = tk.Entry(self.head_lblf, text="Del")
        del_lbl.delete('0', 'end')
        del_lbl.insert('0', "Del")
        del_lbl.configure(state='disabled', width=6, justify='center')
        del_lbl.grid(row=0, column=4)

        ct = 1
        for el in root.findall("Tyre")[0].findall("TyreProfile"):

            lblf = ttk.Labelframe(self.display_port_lbf)
            lblf.configure(cursor='hand2')
            # lblf.grid(row=ct, column=0, columnspan=4, sticky='nsew', padx=20)
            lblf.pack()
            lblf.bind('<Enter>', self.check_row)

            id_ent = tk.Entry(lblf)
            id_ent.delete('0', 'end')
            id_ent.insert('0', str(ct))
            id_ent.configure(state='disabled', width=3, justify='center')
            id_ent.grid(row=0, column=0)

            ty_brd = tk.Entry(lblf)
            ty_brd.delete('0', 'end')
            ty_brd.insert('0', el.attrib['Tyre_brand'])
            ty_brd.configure(state='disabled', justify='center')
            ty_brd.grid(row=0, column=1)

            ty_nm = tk.Entry(lblf)
            ty_nm.delete('0', 'end')
            ty_nm.insert('0', el.attrib['Tyre_name'])
            ty_nm.configure(state='disabled', justify='center')
            ty_nm.grid(row=0, column=2)

            ty_sz = tk.Entry(lblf)
            ty_sz.delete('0', 'end')
            ty_sz.insert('0', el.attrib['Tyre_size'])
            ty_sz.configure(state='disabled', justify='center')
            ty_sz.grid(row=0, column=3)

            del_btn = tk.Button(lblf, text='X', width=4)
            del_btn.configure(state='disabled')
            del_btn.grid(row=0, column=4)
            del_btn.bind('<Button-1>', self.del_row)
            del_btn.bind('<Leave>', self.disable_btn)

            ct += 1

        save_btn = ttk.Button(self.display_port_lbf, text="Save", width=20, command=self.save_display_changes)
        save_btn.pack()

    def load_employee_data(self):
        '''function to populate vehicle data into view port'''

        # Clear viewport first
        self.clear_cfg_display_port()

        # Load Configuration data
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()

        self.head_lblf = ttk.Labelframe(self.display_port_lbf)
        self.head_lblf.configure(text='Employee Information', labelanchor='n')
        # head_lblf.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=20)
        self.head_lblf.pack()

        id_lbl = tk.Entry(self.head_lblf,)
        id_lbl.delete('0', 'end')
        id_lbl.insert('0', "ID")
        id_lbl.configure(state='disabled', width=3, justify='center')
        id_lbl.grid(row=0, column=0)

        emp_nm_lbl = tk.Entry(self.head_lblf, text='Employee Name')
        emp_nm_lbl.delete('0', 'end')
        emp_nm_lbl.insert('0', 'Employee Name')
        emp_nm_lbl.configure(state='disabled', justify='center')
        emp_nm_lbl.grid(row=0, column=1)

        emp_ct_lbl = tk.Entry(self.head_lblf, text='Employee Contact')
        emp_ct_lbl.delete('0', 'end')
        emp_ct_lbl.insert('0', 'Employee Contact')
        emp_ct_lbl.configure(state='disabled', justify='center')
        emp_ct_lbl.grid(row=0, column=2)

        del_lbl = tk.Entry(self.head_lblf, text="Del")
        del_lbl.delete('0', 'end')
        del_lbl.insert('0', "Del")
        del_lbl.configure(state='disabled', width=6, justify='center')
        del_lbl.grid(row=0, column=3)

        ct = 1
        for el in root.findall("Employee")[0].findall("EmployeeProfile"):

            lblf = ttk.Labelframe(self.display_port_lbf)
            lblf.configure(cursor='hand2')
            # lblf.grid(row=ct, column=0, columnspan=4, sticky='nsew', padx=20)
            lblf.pack()
            lblf.bind('<Enter>', self.check_row)

            id_ent = tk.Entry(lblf)
            id_ent.delete('0', 'end')
            id_ent.insert('0', str(ct))
            id_ent.configure(state='disabled', width=3, justify='center')
            id_ent.grid(row=0, column=0)

            emp_nm_ent = tk.Entry(lblf)
            emp_nm_ent.delete('0', 'end')
            emp_nm_ent.insert('0', el.attrib['Emp_name'])
            emp_nm_ent.configure(state='disabled', justify='center')
            emp_nm_ent.grid(row=0, column=1)

            emp_ct_ent = tk.Entry(lblf)
            emp_ct_ent.delete('0', 'end')
            emp_ct_ent.insert('0', el.attrib['Emp_contact'])
            emp_ct_ent.configure(state='disabled', justify='center')
            emp_ct_ent.grid(row=0, column=2)

            del_btn = tk.Button(lblf, text='X', width=4)
            del_btn.configure(state='disabled')
            del_btn.grid(row=0, column=3)
            del_btn.bind('<Button-1>', self.del_row)
            del_btn.bind('<Leave>', self.disable_btn)

            ct += 1

        save_btn = ttk.Button(self.display_port_lbf, text="Save", width=20, command=self.save_display_changes)
        save_btn.pack()

    def check_row(self, evt):
        '''Checks for the labelframe and set a self variable'''
        x,y = self.winfo_pointerxy()
        self.widget_infocus = self.winfo_containing(x,y)
        logger.info(self.widget_infocus.configure()['cursor'][-1])
        if 'hand2' in self.widget_infocus.configure()['cursor']:
            logger.info(f"{self.widget_infocus} is in focus")
            self.btn_widget_infocus = self.widget_infocus.winfo_children()[-1]
            if "X" in self.btn_widget_infocus.configure()['text']:
                self.btn_widget_infocus.configure(state='normal')
                logger.info(f"{self.btn_widget_infocus} is activated")
            else:
                del self.btn_widget
        else:
            del self.widget_infocus

    def del_row(self, evt):
        '''deletes the widget that is set in focus'''
        self.widget_infocus.destroy()

    def disable_btn(self, evt):
        '''disable the button widget that is in focus'''
        self.btn_widget_infocus.configure(state='disabled')

    def save_display_changes(self):
        '''checks for changes in configuration and save changes'''

        widget_ls = self.display_port_lbf.winfo_children()

        # Check which profile is this
        for wg in widget_ls:
            lbl_text = wg.configure('text')[-1]
            if "Vehicle" in lbl_text:
                profile = "Vehicle"
                prof_info = ['Truck_num', 'Trailer_num']
                break
            elif "Tyre" in lbl_text:
                profile = "Tyre"
                prof_info = ['Tyre_brand', 'Tyre_name', 'Tyre_size']
                break
            elif "Employee" in lbl_text:
                profile = "Employee"
                prof_info = ['Emp_name', 'Emp_contact']
                break
            else:
                pass

        logger.info(f"This is a {profile} profile - {prof_info}")

        # Load config file to check
        tree = ET.parse(CONFIG_FILE)
        root = tree.getroot()

        # Checking total count difference between new and old
        profilenode = root.findall(profile)[0]
        org_ent_ct = len(profilenode.findall(f"{profile}Profile"))
        new_ent_ct = len(widget_ls[1:-1])

        if new_ent_ct < org_ent_ct:
            _text_ = f"Updated table has {new_ent_ct} items. Original has {org_ent_ct} items"
            logger.info(_text_)
            if tkMessageBox.askyesno("Attention", f"{_text_}\nDo you want to continue?"):
                logger.info("User continue")

                # Backup original file
                try:
                    shutil.copy(CONFIG_FILE, f"{CONFIG_FILE}.bk{''.join(re.findall('[^ :-]+', str(datetime.now().replace(microsecond=0))))}")
                except Exception as e:
                    logger.exception(f"Error during backup - {e}")

                # Remove Child element from root
                for child in profilenode.findall(f"{profile}Profile"):
                    profilenode.remove(child)

                for wg in widget_ls[1:-1]:
                    pos = 0
                    attrib = {}
                    for child in wg.winfo_children()[1:-1]:
                        attrib[prof_info[pos]] = child.get()
                        pos += 1
                    logger.info(f"Adding attribute to {profilenode} - {attrib}")
                    ET.SubElement(profilenode, f"{profile}Profile", attrib)

                xmlstr = minidom.parseString(ET.tostring(root, encoding='utf8', method='xml'))
                with open(CONFIG_FILE, 'w') as fw:
                    fw.writelines(line+"\n" for line in xmlstr.toprettyxml().split("\n") if not line.strip() == "")
                logger.info("Config updated")

            else:
                logger.info("User Abort")
                tkMessageBox.showinfo("Information", "No changes were made to database")
        else:
            _text_ = "There is no difference in number of items"
            logger.info(_text_)
            tkMessageBox.showinfo("Information", _text_)

    def back_to_main(self):
        if self.controller.check_config_profiles():
            self.controller.show_frame(StartPage)
        else:
            logger.warning("Config validation fail, did not load main page")
            tkMessageBox.showwarning("Warning", "You need to enter at least one entry for each profile\n('Vehicle', 'Tyre', 'Employee').\nPlease check entries using the 'Load / Edit' button for each profile")


# ----- Execution ----- #


if __name__ == "__main__":

    # Create logger
    logger = create_logger(__name__, __file__, __version__, 10)

    # Launch App
    app = TyreApp()
    app.mainloop()
