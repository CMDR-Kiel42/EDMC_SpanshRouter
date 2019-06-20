import Tkinter as tk
import tkFileDialog as filedialog
from ttkHyperlinkLabel import HyperlinkLabel
import sys
import csv
import os
from monitor import monitor

if sys.platform.startswith('linux'):
    import subprocess


this = sys.modules[__name__]
this.next_stop = "No route planned"
this.route = []
this.next_wp_label = "Next waypoint: "
this.parent = None
this.save_route_path = ""


def plugin_start():
    if sys.platform == 'win32':
        this.save_route_path = os.path.expandvars(r'%LOCALAPPDATA%\EDMarketConnector\plugins\SpanshRouter\route.csv')
    else:
        home = os.path.expanduser("~")
        this.save_route_path = home + "/.local/share/EDMarketConnector/plugins/SpanshRouter/route.csv"

    try:
        # Open the last saved route
        with open(this.save_route_path, 'r') as csvfile:
            route_reader = csv.reader(csvfile)
            this.route = [row[0] for row in route_reader]
        
        this.next_stop = this.route[1]
    except:
        print("No previously saved route.")


def plugin_stop():
    if this.route.__len__() != 0:
        # Save route for next time
        with open(this.save_route_path, 'w') as csvfile:
            csvfile.write('\n'.join(this.route))


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


def new_route(self=None):
    filename = filedialog.askopenfilename(filetypes = (("csv files", "*.csv"),))    # show an "Open" dialog box and return the path to the selected file

    if filename.__len__() > 0:
        this.next_route = filename

        with open(filename, 'r') as csvfile:
            route_reader = csv.reader(csvfile)
            this.route = [row[0] for row in route_reader]

        if monitor.system == this.route[1][0]:
            del this.route[1]

        this.next_stop = this.route[1]
        copy_waypoint()
        update_gui()


def update_route():
    del(this.route[1])
    if this.route.__len__() == 0:
        this.next_stop = "No route planned"

        if os.path.isfile(this.save_route_path):
            os.remove(this.save_route_path)
    else:
        this.next_stop = this.route[1]
        update_gui()
        copy_waypoint(this.parent)


def journal_entry(cmdr, is_beta, system, station, entry, state):
    if (entry['event'] == 'FSDJump' or entry['event'] == 'Location') and entry["StarSystem"] == this.next_stop:
        update_route()

def plugin_app(parent):
    this.parent = parent

    this.frame = tk.Frame(parent)
    this.waypoint_btn = tk.Button(this.frame, text=this.next_wp_label + this.next_stop)
    this.upload_route_btn = tk.Button(this.frame, text="Upload new route")

    this.waypoint_btn.bind("<ButtonRelease-1>", copy_waypoint)
    this.upload_route_btn.bind("<ButtonRelease-1>", new_route)

    this.waypoint_btn.pack()
    this.upload_route_btn.pack()

    return this.frame
