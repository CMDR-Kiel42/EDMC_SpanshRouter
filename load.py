import Tkinter as tk
import tkFileDialog as filedialog
import tkMessageBox as confirmDialog
import sys
import csv
import os
import json
import webbrowser
import requests
import traceback
import subprocess
from time import sleep
from SpanshRouter import updater as SpanshUpdater
from SpanshRouter import AutoCompleter
from SpanshRouter import PlaceHolderEntry
from SpanshRouter import SpanshRouter

this = sys.modules[__name__]
spansh_router = None

# Done
def plugin_start(plugin_dir):
    # Check for newer versions
    url = "https://raw.githubusercontent.com/CMDR-Kiel42/EDMC_SpanshRouter/master/version.json"
    try:
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            if this.plugin_version != response.content:
                this.update_available = True
                this.spansh_updater = SpanshUpdater(response.content, plugin_dir)
                
                if not this.spansh_updater.download_zip():
                    sys.stderr.write("Error when downloading the latest SpanshRouter update")
        else:
            sys.stderr.write("Could not query latest SpanshRouter version: " + str(response.status_code) + response.text)
    except NameError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        sys.stderr.write(''.join('!! ' + line for line in lines))
    finally:
        global spansh_router 
        spansh_router = SpanshRouter(plugin_dir)
        spansh_router.open_last_route()

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

    if this.update_available:
        this.spansh_updater.install()

def show_error(error):
    this.error_txt.set(error)
    this.error_lbl.grid()

def hide_error():
    this.error_lbl.grid_remove()

def show_route_gui(show):
    hide_error()
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




def plot_csv(self=None):
    filename = filedialog.askopenfilename(filetypes = (("csv files", "*.csv"),))    # show an "Open" dialog box and return the path to the selected file

    if filename.__len__() > 0:
        with open(filename, 'r') as csvfile:
            route_reader = csv.reader(csvfile)

            # Skip the header
            route_reader.next()

            this.jumps_left = 0
            for row in route_reader:
                if row not in (None, "", []):
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
    hide_error()
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
                
                tries = 0
                while(tries < 20):
                    response = json.loads(results.content)
                    job = response["job"]

                    results_url = "https://spansh.co.uk/api/results/" + job
                    route_response = requests.get(results_url, timeout=5)
                    if route_response.status_code != 202:
                        break
                    tries += 1
                    sleep(1)

                if route_response:
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
                        enable_plot_gui(True)
                        show_error(this.plot_error)
                else:
                    sys.stderr.write("Query to Spansh timed out")
                    enable_plot_gui(True)
                    show_error(this.plot_error)
            else:
                sys.stderr.write("Failed to query route from Spansh: code " + str(results.status_code) + results.text)
                enable_plot_gui(True)
                show_error(this.plot_error)
    except NameError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        sys.stderr.write(''.join('!! ' + line for line in lines))
        enable_plot_gui(True)
        show_error(this.plot_error)

def clear_route(self=None, show_dialog=True):
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
    if (entry['event'] in ['FSDJump', 'Location', 'SupercruiseEntry', 'SupercruiseExit']) and entry["StarSystem"] == this.next_stop:
        update_route()
        this.source_ac.delete(0, tk.END)
        this.source_ac.insert(0, entry["StarSystem"])
        this.source_ac["fg"] = this.source_ac.default_fg_color
    elif entry['event'] == 'FSSDiscoveryScan' and entry['SystemName'] == this.next_stop:
        update_route()

def goto_changelog_page(self=None):
    changelog_url = 'https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/blob/master/CHANGELOG.md#'
    changelog_url += this.spansh_updater.version.replace('.', '')
    webbrowser.open(changelog_url)

def plugin_app(parent):
    