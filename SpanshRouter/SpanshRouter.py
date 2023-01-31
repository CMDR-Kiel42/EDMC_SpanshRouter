import os
import sys
import traceback
import csv
import subprocess
import webbrowser
import json
import re
import requests
import io
from time import sleep
from monitor import monitor
from . import AutoCompleter
from . import PlaceHolder
from .updater import SpanshUpdater
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as confirmDialog
from config import appname


class SpanshRouter():
    def __init__(self, plugin_dir):
        version_file = os.path.join(plugin_dir, "version.json")
        with open(version_file, 'r') as version_fd:
            self.plugin_version = version_fd.read()

        self.update_available = False
        self.next_stop = "No route planned"
        self.route = []
        self.next_wp_label = "Next waypoint: "
        self.jumpcountlbl_txt = "Estimated jumps left: "
        self.parent = None
        self.plugin_dir = plugin_dir
        self.save_route_path = os.path.join(plugin_dir, 'route.csv')
        self.offset_file_path = os.path.join(plugin_dir, 'offset')
        self.offset = 0
        self.jumps_left = 0
        self.error_txt = tk.StringVar()
        self.plot_error = "Error while trying to plot a route, please try again."
        self.system_header = "System Name"
        self.jumps_header = "Jumps"
        
    #   -- GUI part --
    def init_gui(self, parent,IFFSQR):
        self.parent = parent
        self.frame = tk.Frame(IFFSQR)
        #self.frame = tk.Frame(parent, borderwidth=2)
        
        self.frame.grid(sticky=tk.NSEW, columnspan=2)
        
        # Route info
        self.waypoint_prev_btn = tk.Button(self.frame, text="^", command=self.goto_prev_waypoint)
        self.waypoint_btn = tk.Button(self.frame, text=self.next_wp_label + self.next_stop, command=self.copy_waypoint)
        self.waypoint_next_btn = tk.Button(self.frame, text="v", command=self.goto_next_waypoint)
        self.jumpcounttxt_lbl = tk.Label(self.frame, text=self.jumpcountlbl_txt + str(self.jumps_left))
        self.error_lbl = tk.Label(self.frame, textvariable=self.error_txt)

        # Plotting GUI
        self.source_ac = AutoCompleter(self.frame, "Source System", width=30)
        self.dest_ac = AutoCompleter(self.frame, "Destination System", width=30)
        self.range_entry = PlaceHolder(self.frame, "Range (LY)", width=10)
        self.efficiency_slider = tk.Scale(self.frame, from_=1, to=100, orient=tk.HORIZONTAL, label="Efficiency (%)")
        self.efficiency_slider.set(60)
        self.plot_gui_btn = tk.Button(self.frame, text="Plot route", command=self.show_plot_gui)
        self.plot_route_btn = tk.Button(self.frame, text="Calculate", command=self.plot_route)
        self.cancel_plot = tk.Button(self.frame, text="Cancel", command=lambda: self.show_plot_gui(False))

        self.csv_route_btn = tk.Button(self.frame, text="Import file", command=self.plot_file)
        self.clear_route_btn = tk.Button(self.frame, text="Clear route", command=self.clear_route)

        row = 0
        self.waypoint_prev_btn.grid(row=row, columnspan=2)
        row += 1
        self.waypoint_btn.grid(row=row, columnspan=2)
        row += 1
        self.waypoint_next_btn.grid(row=row, columnspan=2)
        row += 1
        self.source_ac.grid(row=row,columnspan=2, pady=(10,0)) # The AutoCompleter takes two rows to show the list when needed, so we skip one
        row += 2 
        self.dest_ac.grid(row=row,columnspan=2, pady=(10,0))
        row += 2 
        self.range_entry.grid(row=row, pady=10, sticky=tk.W)
        row += 1
        self.efficiency_slider.grid(row=row, pady=10, columnspan=2, sticky=tk.EW)
        row += 1
        self.csv_route_btn.grid(row=row, pady=10, padx=0)
        self.plot_route_btn.grid(row=row, pady=10, padx=0)
        self.plot_gui_btn.grid(row=row, column=1, pady=10, padx=5, sticky=tk.W)
        self.cancel_plot.grid(row=row, column=1, pady=10, padx=5, sticky=tk.E)
        row += 1
        self.clear_route_btn.grid(row=row,column=1)
        row += 1
        self.jumpcounttxt_lbl.grid(row=row, pady=5, sticky=tk.W)
        row += 1
        self.error_lbl.grid(row=row, columnspan=2)
        self.error_lbl.grid_remove()
        row += 1

        # Check if we're having a valid range on the fly
        self.range_entry.var.trace('w', self.check_range)

        self.show_plot_gui(False)

        if not self.route.__len__() > 0:
            self.waypoint_prev_btn.grid_remove()
            self.waypoint_btn.grid_remove()
            self.waypoint_next_btn.grid_remove()
            self.jumpcounttxt_lbl.grid_remove()
            self.clear_route_btn.grid_remove()

        self.update_gui()

        return self.frame

    def show_plot_gui(self, show=True):
        if show:
            self.waypoint_prev_btn.grid_remove()
            self.waypoint_btn.grid_remove()
            self.waypoint_next_btn.grid_remove()
            self.jumpcounttxt_lbl.grid_remove()
            self.clear_route_btn.grid_remove()

            self.plot_gui_btn.grid_remove()
            self.csv_route_btn.grid_remove()
            self.source_ac.grid()
            # Prefill the "Source" entry with the current system
            # LF self.source_ac.set_text(monitor.system if monitor.system is not None else "Source System", monitor.system is None)   
            
            self.dest_ac.grid()
            self.range_entry.grid()
            self.efficiency_slider.grid()
            self.plot_route_btn.grid()
            self.cancel_plot.grid()

            self.show_route_gui(False)

        else:
            if len(self.source_ac.var.get()) == 0:
                self.source_ac.put_placeholder()
            if len(self.dest_ac.var.get()) == 0:
                self.dest_ac.put_placeholder()
            self.source_ac.hide_list()
            self.source_ac.grid_remove()
            self.dest_ac.hide_list()
            self.dest_ac.grid_remove()
            self.range_entry.grid_remove()
            self.efficiency_slider.grid_remove()
            self.plot_gui_btn.grid_remove()
            self.plot_route_btn.grid_remove()
            self.cancel_plot.grid_remove()
            self.plot_gui_btn.grid()
            self.csv_route_btn.grid()
            self.show_route_gui(True)

    def set_source_ac(self, text):
        self.source_ac.delete(0, tk.END)
        self.source_ac.insert(0, text)
        self.source_ac.set_default_style()

    def show_route_gui(self, show):
        self.hide_error()
        if not show or not self.route.__len__() > 0:
            self.waypoint_prev_btn.grid_remove()
            self.waypoint_btn.grid_remove()
            self.waypoint_next_btn.grid_remove()
            self.jumpcounttxt_lbl.grid_remove()
            self.clear_route_btn.grid_remove()
        else:
            self.waypoint_btn["text"] = self.next_wp_label + self.next_stop
            if self.jumps_left > 0:
                self.jumpcounttxt_lbl["text"] = self.jumpcountlbl_txt + str(self.jumps_left)
                self.jumpcounttxt_lbl.grid()
            else:
                self.jumpcounttxt_lbl.grid_remove()

            self.waypoint_prev_btn.grid()
            self.waypoint_btn.grid()
            self.waypoint_next_btn.grid()

            if self.offset == 0:
                self.waypoint_prev_btn.config(state=tk.DISABLED)
            else:
                self.waypoint_prev_btn.config(state=tk.NORMAL)

                if self.offset == self.route.__len__()-1:
                    self.waypoint_next_btn.config(state=tk.DISABLED)
                else:
                    self.waypoint_next_btn.config(state=tk.NORMAL)

            self.clear_route_btn.grid()

    def update_gui(self):
        self.show_route_gui(True)

    def show_error(self, error):
        self.error_txt.set(error)
        self.error_lbl.grid()

    def hide_error(self):
        self.error_lbl.grid_remove()

    def enable_plot_gui(self, enable):
        if enable:
            self.source_ac.config(state=tk.NORMAL)
            self.source_ac.update_idletasks()
            self.dest_ac.config(state=tk.NORMAL)
            self.dest_ac.update_idletasks()
            self.efficiency_slider.config(state=tk.NORMAL)
            self.efficiency_slider.update_idletasks()
            self.range_entry.config(state=tk.NORMAL)
            self.range_entry.update_idletasks()
            self.plot_route_btn.config(state=tk.NORMAL, text="Calculate")
            self.plot_route_btn.update_idletasks()
            self.cancel_plot.config(state=tk.NORMAL)
            self.cancel_plot.update_idletasks()
        else:
            self.source_ac.config(state=tk.DISABLED)
            self.source_ac.update_idletasks()
            self.dest_ac.config(state=tk.DISABLED)
            self.dest_ac.update_idletasks()
            self.efficiency_slider.config(state=tk.DISABLED)
            self.efficiency_slider.update_idletasks()
            self.range_entry.config(state=tk.DISABLED)
            self.range_entry.update_idletasks()
            self.plot_route_btn.config(state=tk.DISABLED, text="Computing...")
            self.plot_route_btn.update_idletasks()
            self.cancel_plot.config(state=tk.DISABLED)
            self.cancel_plot.update_idletasks()

    #   -- END GUI part --


    def open_last_route(self):
        try:
            has_headers = False
            with open(self.save_route_path, 'r') as csvfile:
                # Check if the file has a header for compatibility with previous versions
                dict_route_reader = csv.DictReader(csvfile)
                if dict_route_reader.fieldnames[0] == self.system_header:
                    has_headers = True

            if has_headers:
                self.plot_csv(self.save_route_path, clear_previous_route=False)
            else:
                with open(self.save_route_path, 'r') as csvfile:
                    route_reader = csv.reader(csvfile)

                    for row in route_reader:
                        if row not in (None, "", []):
                            self.route.append(row)

            try:
                with open(self.offset_file_path, 'r') as offset_fh:
                    self.offset = int(offset_fh.readline())

            except:
                self.offset = 0

            self.jumps_left = 0
            for row in self.route[self.offset:]:
                if row[1] not in [None, "", []]:
                    self.jumps_left += int(row[1])

            self.next_stop = self.route[self.offset][0]
            self.copy_waypoint()
            self.update_gui()

        except IOError:
            print("No previously saved route.")
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))

    def copy_waypoint(self):
        if sys.platform == "linux" or sys.platform == "linux2":
            command = subprocess.Popen(["echo", "-n", self.next_stop], stdout=subprocess.PIPE)
            subprocess.Popen(["xclip", "-selection", "c"], stdin=command.stdout)
        else:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(self.next_stop)
            self.parent.update()

    def goto_next_waypoint(self):
        if self.offset < self.route.__len__()-1:
            self.update_route(1)

    def goto_prev_waypoint(self):
        if self.offset > 0:
            self.update_route(-1)

    def update_route(self, direction=1):
        if direction > 0:
            if self.route[self.offset][1] not in [None, "", []]:
                self.jumps_left -= int(self.route[self.offset][1])
            self.offset += 1
        else:
            self.offset -= 1
            if self.route[self.offset][1] not in [None, "", []]:
                self.jumps_left += int(self.route[self.offset][1])

        if self.offset >= self.route.__len__():
            self.next_stop = "End of the road!"
            self.update_gui()
        else:
            self.next_stop = self.route[self.offset][0]
            self.update_gui()
            self.copy_waypoint()
        self.save_offset()

    def goto_changelog_page(self):
        changelog_url = 'https://github.com/CMDR-Kiel42/EDMC_SpanshRouter/blob/master/CHANGELOG.md#'
        changelog_url += self.spansh_updater.version.replace('.', '')
        webbrowser.open(changelog_url)

    def plot_file(self):
        ftypes = [
            ('All supported files', '*.csv *.txt'),
            ('CSV files', '*.csv'),
            ('Text files', '*.txt'),
        ]
        filename = filedialog.askopenfilename(filetypes = ftypes, initialdir=os.path.expanduser('~'))

        if filename.__len__() > 0:
            try:
                ftype_supported = False
                if filename.endswith(".csv"):
                    ftype_supported = True
                    self.plot_csv(filename)

                elif filename.endswith(".txt"):
                    ftype_supported = True
                    self.plot_edts(filename)

                if ftype_supported:
                    self.offset = 0
                    self.next_stop = self.route[0][0]
                    self.copy_waypoint()
                    self.update_gui()
                    self.save_all_route()
                else:
                    self.show_error("Unsupported file type")
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                sys.stderr.write(''.join('!! ' + line for line in lines))
                self.enable_plot_gui(True)
                self.show_error("An error occured while reading the file.")
                

    def plot_csv(self, filename, clear_previous_route=True):
        
        with io.open(filename, 'r', encoding='utf-8-sig') as csvfile:
            route_reader = csv.DictReader(csvfile)
            if clear_previous_route:
                self.clear_route(False)
            for row in route_reader:
                if row not in (None, "", []):
                    self.route.append([
                        row[self.system_header],
                        row.get(self.jumps_header, "") # Jumps column is optional
                    ])
                    if row.get(self.jumps_header) != None:
                        self.jumps_left += int(row[self.jumps_header])

    def plot_route(self):
        self.hide_error()
        try:
            source = self.source_ac.get().strip()
            dest = self.dest_ac.get().strip()
            efficiency = self.efficiency_slider.get()

            # Hide autocomplete lists in case they're still shown
            self.source_ac.hide_list()
            self.dest_ac.hide_list()

            if (    source  and source != self.source_ac.placeholder and
                    dest    and dest != self.dest_ac.placeholder    ):

                try:
                    range_ly = float(self.range_entry.get())
                except ValueError:
                    self.show_error("Invalid range")
                    return

                job_url="https://spansh.co.uk/api/route?"

                results = requests.post(job_url, params={
                    "efficiency": efficiency,
                    "range": range_ly,
                    "from": source,
                    "to": dest
                }, headers={'User-Agent': "EDMC_SpanshRouter 1.0"})

                if results.status_code == 202:
                    self.enable_plot_gui(False)

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
                            self.clear_route(show_dialog=False)
                            for waypoint in route:
                                self.route.append([waypoint["system"], str(waypoint["jumps"])])
                                self.jumps_left += waypoint["jumps"]
                            self.enable_plot_gui(True)
                            self.show_plot_gui(False)
                            self.offset = 1 if self.route[0][0] == monitor.system else 0
                            self.next_stop = self.route[self.offset][0]
                            self.copy_waypoint()
                            self.update_gui()
                            self.save_all_route()
                        else:
                            sys.stderr.write("Failed to query plotted route from Spansh: code " + str(route_response.status_code) + route_response.text + '\n')
                            self.enable_plot_gui(True)
                            failure = json.loads(results.content)

                            if route_response.status_code == 400 and "error" in failure:
                                self.show_error(failure["error"])
                                if "starting system" in failure["error"]:
                                    self.source_ac["fg"] = "red"
                                if "finishing system" in failure["error"]:
                                    self.dest_ac["fg"] = "red"
                            else:
                                self.show_error(self.plot_error)
                    else:
                        sys.stderr.write("Query to Spansh timed out")
                        self.enable_plot_gui(True)
                        self.show_error("The query to Spansh was too long and timed out, please try again.")
                else:
                    sys.stderr.write("Failed to query plotted route from Spansh: code " + str(results.status_code) + results.text + '\n')
                    self.enable_plot_gui(True)
                    failure = json.loads(results.content)

                    if results.status_code == 400 and "error" in failure:
                        self.show_error(failure["error"])
                        if "starting system" in failure["error"]:
                            self.source_ac["fg"] = "red"
                        if "finishing system" in failure["error"]:
                            self.dest_ac["fg"] = "red"
                    else:
                        self.show_error(self.plot_error)

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))
            self.enable_plot_gui(True)
            self.show_error(self.plot_error)

    def plot_edts(self, filename):
        try:
            with open(filename, 'r') as txtfile:
                route_txt = txtfile.readlines()
                self.clear_route(False)
                for row in route_txt:
                    if row not in (None, "", []):
                        if row.lstrip().startswith('==='):
                            jumps = int(re.findall("\d+ jump", row)[0].rstrip(' jumps'))
                            self.jumps_left += jumps

                            system = row[row.find('>') + 1:]
                            if ',' in system:
                                systems = system.split(',')
                                for system in systems:
                                    self.route.append([system.strip(), jumps])
                                    jumps = 1
                                    self.jumps_left += jumps
                            else:
                                self.route.append([system.strip(), jumps])
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))
            self.enable_plot_gui(True)
            self.show_error("An error occured while reading the file.")

    def clear_route(self, show_dialog=True):
        clear = confirmDialog.askyesno("SpanshRouter","Are you sure you want to clear the current route?") if show_dialog else True

        if clear:
            self.offset = 0
            self.route = []
            self.next_waypoint = ""
            self.jumps_left = 0
            try:
                os.remove(self.save_route_path)
            except:
                print("No route to delete")
            try:
                os.remove(self.offset_file_path)
            except:
                print("No offset file to delete")

            self.update_gui()

    def save_all_route(self):
        self.save_route()
        self.save_offset()

    def save_route(self):
        if self.route.__len__() != 0:
            with open(self.save_route_path, 'w') as csvfile:
                fieldnames = [self.system_header, self.jumps_header]
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                writer.writerows(self.route)
        else:
            try:
                os.remove(self.save_route_path)
            except:
                print("No route to delete")

    def save_offset(self):
        if self.route.__len__() != 0:
            with open(self.offset_file_path, 'w') as offset_fh:
                offset_fh.write(str(self.offset))
        else:
            try:
                os.remove(self.offset_file_path)
            except:
                print("No offset to delete")

    def check_range(self, name, index, mode):
        value = self.range_entry.var.get()
        if value.__len__() > 0 and value != self.range_entry.placeholder:
            try:
                float(value)
                self.range_entry.set_error_style(False)
                self.hide_error()
            except ValueError:
                self.show_error("Invalid range")
                self.range_entry.set_error_style()

    def cleanup_old_version(self):
        try:
            if (os.path.exists(os.path.join(self.plugin_dir, "AutoCompleter.py"))
            and os.path.exists(os.path.join(self.plugin_dir, "SpanshRouter"))):
                files_list = os.listdir(self.plugin_dir)

                for filename in files_list:
                    if (filename != "load.py"
                    and (filename.endswith(".py") or filename.endswith(".pyc") or filename.endswith(".pyo"))):
                        os.remove(os.path.join(self.plugin_dir, filename))
        except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                sys.stderr.write(''.join('!! ' + line for line in lines))

    def check_for_update(self):
        self.cleanup_old_version()
        version_url = "https://raw.githubusercontent.com/CMDR-Kiel42/EDMC_SpanshRouter/master/version.json"
        try:
            response = requests.get(version_url, timeout=2)
            if response.status_code == 200:
                if self.plugin_version != response.text:
                    self.update_available = True
                    self.spansh_updater = SpanshUpdater(response.text, self.plugin_dir)

            else:
                sys.stderr.write("Could not query latest SpanshRouter version: " + str(response.status_code) + response.text)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            sys.stderr.write(''.join('!! ' + line for line in lines))

    def install_update(self):
        self.spansh_updater.install()
