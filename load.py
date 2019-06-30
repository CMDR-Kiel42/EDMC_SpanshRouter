import Tkinter as tk
import tkFileDialog as filedialog
from ttkHyperlinkLabel import HyperlinkLabel
import sys
import csv
import os
from monitor import monitor
import urllib
import json

if sys.platform.startswith('linux'):
    import subprocess


this = sys.modules[__name__]
this.plugin_version = "1.1.0"
this.update_available = False
this.next_stop = "No route planned"
this.route = []
this.next_wp_label = "Next waypoint: "
this.parent = None
this.save_route_path = ""
this.offset = 1


def plugin_start(plugin_dir):
    # Check for newer versions
    url = "https://raw.githubusercontent.com/CMDR-Kiel42/EDMC_SpanshRouter/master/version.json"
    response = urllib.urlopen(url)
    latest_version = response.read()

    if response.code == 200 and this.plugin_version != latest_version:
        this.update_available = True

    this.save_route_path = os.path.join(plugin_dir, 'route.csv')

    try:
        # Open the last saved route
        with open(this.save_route_path, 'r') as csvfile:
            route_reader = csv.reader(csvfile)

            i = 0
            for row in route_reader:
                this.route.append(row)
                if row[1] == 'x':
                    this.offset = i
                i+=1
        
        this.route[this.offset][1] = ''
        this.next_stop = this.route[this.offset][0]
        copy_waypoint()
    except:
        print("No previously saved route.")


def plugin_stop():
    if this.route.__len__() != 0:
        # Save route for next time
        if this.offset < this.route.__len__():
            this.route[this.offset][1] = 'x'
        with open(this.save_route_path, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(this.route)


def update_gui():
    this.waypoint_btn["text"] = this.next_wp_label + this.next_stop


def copy_waypoint(self=None):
    if sys.platform == "win32":
        this.parent.clipboard_clear()
        this.parent.clipboard_append(this.next_stop)
        this.parent.update()
    else:
        command = subprocess.Popen(["echo", "-n", this.next_stop], stdout=subprocess.PIPE)
        subprocess.Popen(["xclip", "-selection", "c"], stdin=command.stdout)

def goto_next_waypoint(self=None):
    if this.offset < this.route.__len__():
        update_route()

def goto_prev_waypoint(self=None):
    if this.offset > 0:
        this.offset -= 2    # update_route() starts by incrementing the offset, so we can decrement by 2
        update_route()

def new_route(self=None):
    filename = filedialog.askopenfilename(filetypes = (("csv files", "*.csv"),))    # show an "Open" dialog box and return the path to the selected file

    if filename.__len__() > 0:
        with open(filename, 'r') as csvfile:
            route_reader = csv.reader(csvfile)
            this.route = [[row[0], ''] for row in route_reader]

            # Remove the CSV header
            del this.route[0]

        this.offset = 0
        this.next_stop = this.route[1][0]
        copy_waypoint()
        update_gui()


def update_route():
    this.offset += 1
    if this.offset >= this.route.__len__():
        this.next_stop = "End of the road!"
        update_gui()
    else:
        this.next_stop = this.route[this.offset][0]
        update_gui()
        copy_waypoint(this.parent)


def journal_entry(cmdr, is_beta, system, station, entry, state):
    if (entry['event'] == 'FSDJump' or entry['event'] == 'Location') and entry["StarSystem"] == this.next_stop:
        update_route()
    elif entry['event'] in ['SupercruiseEntry', 'SupercruiseExit'] and entry['StarSystem'] == this.next_stop:
        update_route()
    elif entry['event'] == 'FSSDiscoveryScan' and entry['SystemName'] == this.next_stop:
        update_route()


def plugin_app(parent):
    this.parent = parent

    this.frame = tk.Frame(parent)
    this.waypoint_prev_btn = tk.Button(this.frame, text="^")
    this.waypoint_btn = tk.Button(this.frame, text=this.next_wp_label + this.next_stop)
    this.waypoint_next_btn = tk.Button(this.frame, text="v")

    this.upload_route_btn = tk.Button(this.frame, text="Upload new route")

    this.waypoint_prev_btn.bind("<ButtonRelease-1>", goto_prev_waypoint)
    this.waypoint_btn.bind("<ButtonRelease-1>", copy_waypoint)
    this.waypoint_next_btn.bind("<ButtonRelease-1>", goto_next_waypoint)
    this.upload_route_btn.bind("<ButtonRelease-1>", new_route)

    this.waypoint_prev_btn.pack()
    this.waypoint_btn.pack()
    this.waypoint_next_btn.pack()    
    this.upload_route_btn.pack()
    
    if this.update_available:
        this.update_lbl = tk.Label(this.frame, text="SpanshRouter update available for download!")
        this.update_lbl.pack()

    return this.frame
