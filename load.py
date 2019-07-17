import Tkinter as tk
import tkFileDialog as filedialog
import tkMessageBox as confirmDialog
import sys
import csv
import os
import urllib
import json
import webbrowser
import requests
from AutoCompleter import AutoCompleter
from PlaceHolderEntry import PlaceHolderEntry

if sys.platform.startswith('linux'):
    import subprocess


this = sys.modules[__name__]
this.plugin_version = "1.2.1"
this.update_available = False
this.next_stop = "No route planned"
this.route = []
this.next_wp_label = "Next waypoint: "
this.jumpcountlbl_txt = "Estimated jumps left: "
this.parent = None
this.save_route_path = ""
this.offset_file_path = ""
this.offset = 0
this.jumps_left = 0


def plugin_start(plugin_dir):
    # Check for newer versions
    url = "https://raw.githubusercontent.com/CMDR-Kiel42/EDMC_SpanshRouter/master/version.json"
    response = urllib.urlopen(url)
    latest_version = response.read()

    if response.code == 200 and this.plugin_version != latest_version:
        this.update_available = True

    this.save_route_path = os.path.join(plugin_dir, 'route.csv')
    this.offset_file_path = os.path.join(plugin_dir, 'offset')

    try:
        # Open the last saved route
        with open(this.save_route_path, 'r') as csvfile:
            route_reader = csv.reader(csvfile)

            for row in route_reader:
                this.route.append(row)

            try:
                with open(this.offset_file_path, 'r') as offset_fh:
                    this.offset = int(offset_fh.readline())

            except:
                this.offset = 0

        for row in this.route[this.offset:]:
            this.jumps_left += int(row[1])

        this.next_stop = this.route[this.offset][0]
        copy_waypoint()
    except:
        print("No previously saved route.")


def plugin_stop():
    if this.route.__len__() != 0:
        # Save route for next time
        with open(this.save_route_path, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(this.route)

        with open(this.offset_file_path, 'w') as offset_fh:
            offset_fh.write(str(this.offset))
    else:
        try:
            os.remove(this.save_route_path)
            os.remove(this.offset_file_path)
        except:
            print("No route to delete")


def show_route_gui(show):
    if not show or not this.route.__len__() > 0:
        this.waypoint_prev_btn.grid_remove()
        this.waypoint_btn.grid_remove()
        this.waypoint_next_btn.grid_remove()
        this.jumpcounttxt_lbl.grid_remove()
        this.clear_route_btn.grid_remove()
    else:
        this.waypoint_btn["text"] = this.next_wp_label + this.next_stop
        this.jumpcounttxt_lbl["text"] = this.jumpcountlbl_txt + str(this.jumps_left)
        this.jumpcounttxt_lbl.grid()

        this.waypoint_prev_btn.grid()
        this.waypoint_btn.grid()
        this.waypoint_next_btn.grid()

        if this.offset == 0:
            this.waypoint_prev_btn.config(state=tk.DISABLED)
        else:
            this.waypoint_prev_btn.config(state=tk.NORMAL)

            if this.offset == this.route.__len__()-1:
                this.waypoint_next_btn.config(state=tk.DISABLED)
            else:
                this.waypoint_next_btn.config(state=tk.NORMAL)

        this.clear_route_btn.grid()

def update_gui():
    show_route_gui(True)

def show_plot_gui(show=True):
    if show:
        this.waypoint_prev_btn.grid_remove()
        this.waypoint_btn.grid_remove()
        this.waypoint_next_btn.grid_remove()
        this.jumpcounttxt_lbl.grid_remove()
        this.clear_route_btn.grid_remove()

        this.plot_gui_btn.grid_remove()
        this.csv_route_btn.grid_remove()
        this.source_ac.grid()
        this.dest_ac.grid()
        this.range_entry.grid()
        this.efficiency_slider.grid()
        this.plot_route_btn.grid()
        this.cancel_plot.grid()

        # Workaround because EDMC keeps switching the placeholder to bright white
        if this.source_ac.get() == this.source_ac.placeholder:
            this.source_ac.force_placeholder_color()
        if this.dest_ac.get() == this.dest_ac.placeholder:
            this.dest_ac.force_placeholder_color()
        if this.range_entry.get() == this.range_entry.placeholder:
            this.range_entry.force_placeholder_color()
        show_route_gui(False)

    else:
        this.source_ac.put_placeholder()
        this.dest_ac.put_placeholder()
        this.source_ac.grid_remove()
        this.dest_ac.grid_remove()
        this.range_entry.grid_remove()
        this.efficiency_slider.grid_remove()
        this.plot_gui_btn.grid_remove()
        this.plot_route_btn.grid_remove()
        this.cancel_plot.grid_remove()
        this.plot_gui_btn.grid()
        this.csv_route_btn.grid()
        show_route_gui(True)

def copy_waypoint(self=None):
    if sys.platform == "win32":
        this.parent.clipboard_clear()
        this.parent.clipboard_append(this.next_stop)
        this.parent.update()
    else:
        command = subprocess.Popen(["echo", "-n", this.next_stop], stdout=subprocess.PIPE)
        subprocess.Popen(["xclip", "-selection", "c"], stdin=command.stdout)

def goto_next_waypoint(self=None):
    if this.offset < this.route.__len__()-1:
        update_route(1)

def goto_prev_waypoint(self=None):
    if this.offset > 0:
        update_route(-1)

def plot_csv(self=None):
    filename = filedialog.askopenfilename(filetypes = (("csv files", "*.csv"),))    # show an "Open" dialog box and return the path to the selected file

    if filename.__len__() > 0:
        with open(filename, 'r') as csvfile:
            route_reader = csv.reader(csvfile)

            # Skip the header
            route_reader.next()

            this.jumps_left = 0
            for row in route_reader:
                this.route.append([row[0], row[4]])
                this.jumps_left += int(row[4])

        this.offset = 0
        this.next_stop = this.route[0][0]
        copy_waypoint()
        update_gui()

def enable_plot_gui(enable):
    if enable:
        this.source_ac.config(state=tk.NORMAL)
        this.source_ac.update_idletasks()
        this.dest_ac.config(state=tk.NORMAL)
        this.dest_ac.update_idletasks()
        this.efficiency_slider.config(state=tk.NORMAL)
        this.efficiency_slider.update_idletasks()
        this.range_entry.config(state=tk.NORMAL)
        this.range_entry.update_idletasks()
        this.plot_route_btn.config(state=tk.NORMAL, text="Calculate")
        this.plot_route_btn.update_idletasks()
        this.cancel_plot.config(state=tk.NORMAL)
        this.cancel_plot.update_idletasks()
    else:
        this.source_ac.config(state=tk.DISABLED)
        this.source_ac.update_idletasks()
        this.dest_ac.config(state=tk.DISABLED)
        this.dest_ac.update_idletasks()
        this.efficiency_slider.config(state=tk.DISABLED)
        this.efficiency_slider.update_idletasks()
        this.range_entry.config(state=tk.DISABLED)
        this.range_entry.update_idletasks()
        this.plot_route_btn.config(state=tk.DISABLED, text="Computing...")
        this.plot_route_btn.update_idletasks()
        this.cancel_plot.config(state=tk.DISABLED)
        this.cancel_plot.update_idletasks()

def plot_route(self=None):
    try:
        source = this.source_ac.get()
        dest = this.dest_ac.get()
        efficiency = this.efficiency_slider.get()

        if (    source  and source != this.source_ac.placeholder and
                dest    and dest != this.dest_ac.placeholder    ):
            range_ly = float(this.range_entry.get())

            job_url="https://spansh.co.uk/api/route?"

            results = requests.post(job_url, params={
                "efficiency": efficiency,
                "range": range_ly,
                "from": source,
                "to": dest
            }, headers={'User-Agent': "EDMC_SpanshRouter 1.0"})

            if results.status_code == 202:
                enable_plot_gui(False)

                while(True):
                    response = json.loads(results.content)
                    job = response["job"]

                    results_url = "https://spansh.co.uk/api/results/" + job
                    route_response = requests.get(results_url)
                    if route_response.status_code != 202:
                        break

                if route_response.status_code == 200:
                    route = json.loads(route_response.content)["result"]["system_jumps"]
                    clear_route(show_dialog=False)
                    for waypoint in route:
                        this.route.append([waypoint["system"], str(waypoint["jumps"])])
                        this.jumps_left += waypoint["jumps"]
                    enable_plot_gui(True)
                    show_plot_gui(False)
                    this.offset = 0
                    this.next_stop = this.route[0][0]
                    copy_waypoint()
                    update_gui()
                else:
                    sys.stderr.write("Failed to query plotted route from Spansh: code " + str(route_response.status_code) + route_response.text)
            else:
                sys.stderr.write("Failed to query route from Spansh: code " + str(results.status_code) + results.text)

    except:
        pass

def clear_route(self=None, show_dialog=True):
    print("Show dialog =" + str(show_dialog))
    clear = confirmDialog.askyesno("SpanshRouter","Are you sure you want to clear the current route?") if show_dialog else True

    if clear:
        this.offset = 0
        this.route = []
        this.next_waypoint = ""
        this.jumps_left = 0
        try:
            os.remove(this.save_route_path)
        except:
            print("No route to delete")
        try:
            os.remove(this.offset_file_path)
        except:
            print("No offset file to delete")

        update_gui()

def update_route(direction=1):
    if direction > 0:
        this.jumps_left -= int(this.route[this.offset][1])
        this.offset += 1
    else:
        this.offset -= 1
        this.jumps_left += int(this.route[this.offset][1])

    if this.offset >= this.route.__len__():
        this.next_stop = "End of the road!"
        update_gui()
    else:
        this.next_stop = this.route[this.offset][0]
        update_gui()
        copy_waypoint(this.parent)

def journal_entry(cmdr, is_beta, system, station, entry, state):
    if entry["StarSystem"]:
        this.source_ac.delete(0, tk.END)
        this.source_ac.insert(0, entry["StarSystem"])
        this.source_ac["fg"] = this.source_ac.default_fg_color
    if (entry['event'] == 'FSDJump' or entry['event'] == 'Location') and entry["StarSystem"] == this.next_stop:
        update_route()
    elif entry['event'] in ['SupercruiseEntry', 'SupercruiseExit'] and entry['StarSystem'] == this.next_stop:
        update_route()
    elif entry['event'] == 'FSSDiscoveryScan' and entry['SystemName'] == this.next_stop:
        update_route()

def goto_update_page(self=None):
    webbrowser.open('https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/releases')

def plugin_app(parent):
    this.parent = parent
    parentwidth = parent.winfo_width()
    this.frame = tk.Frame(parent, borderwidth=2)
    this.frame.grid(sticky=tk.NSEW)

    # Route info
    this.waypoint_prev_btn = tk.Button(this.frame, text="^", command=goto_prev_waypoint)
    this.waypoint_btn = tk.Button(this.frame, text=this.next_wp_label + this.next_stop, command=copy_waypoint)
    this.waypoint_next_btn = tk.Button(this.frame, text="v", command=goto_next_waypoint)
    this.jumpcounttxt_lbl = tk.Label(this.frame, text=this.jumpcountlbl_txt + str(this.jumps_left))

    # Plotting GUI
    this.source_ac = AutoCompleter(this.frame, "Source System", width=30)
    this.dest_ac = AutoCompleter(this.frame, "Destination System", width=30)
    this.range_entry = PlaceHolderEntry(this.frame, "Range (LY)", width=10)
    this.efficiency_slider = tk.Scale(this.frame, from_=1, to=100, orient=tk.HORIZONTAL, label="Efficiency (%)")
    this.efficiency_slider.set(60)
    this.plot_gui_btn = tk.Button(this.frame, text="Plot route", command=show_plot_gui)
    this.plot_route_btn = tk.Button(this.frame, text="Calculate", command=plot_route)
    this.cancel_plot = tk.Button(this.frame, text="Cancel", command=lambda: show_plot_gui(False))
    
    this.csv_route_btn = tk.Button(this.frame, text="Import CSV", command=plot_csv)
    this.clear_route_btn = tk.Button(this.frame, text="Clear route", command=clear_route)

    row = 0
    this.waypoint_prev_btn.grid(row=row, columnspan=2)
    row += 1
    this.waypoint_btn.grid(row=row, columnspan=2)
    row += 1
    this.waypoint_next_btn.grid(row=row, columnspan=2)
    row += 1
    this.source_ac.grid(row=row,columnspan=2, pady=(10,0)) # The AutoCompleter takes two rows to show the list when needed, so we skip one
    row += 2
    this.dest_ac.grid(row=row,columnspan=2, pady=(10,0))
    row += 2
    this.range_entry.grid(row=row, pady=10, sticky=tk.W)
    row += 1
    this.efficiency_slider.grid(row=row, pady=10, columnspan=2, sticky=tk.EW)
    row += 1
    this.csv_route_btn.grid(row=row, pady=10, padx=0)
    this.plot_route_btn.grid(row=row, pady=10, padx=0)
    this.plot_gui_btn.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
    this.cancel_plot.grid(row=row, column=1, pady=10, padx=5, sticky=tk.E)
    row += 1
    this.clear_route_btn.grid(row=row,column=1)
    row += 1
    this.jumpcounttxt_lbl.grid(row=row, pady=5, sticky=tk.W)
    row += 1

    show_plot_gui(False)

    if not this.route.__len__() > 0:
        this.waypoint_prev_btn.grid_remove()
        this.waypoint_btn.grid_remove()
        this.waypoint_next_btn.grid_remove()
        this.jumpcounttxt_lbl.grid_remove()
        this.clear_route_btn.grid_remove()

    if this.update_available:
        this.update_btn = tk.Button(this.frame, text="SpanshRouter update available for download!", command=goto_update_page)
        this.update_btn.grid(row=row, pady=5, columnspan=2)
        row += 1

    update_gui()

    return this.frame
