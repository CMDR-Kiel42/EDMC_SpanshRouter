#! /usr/bin/env python2

import os
import sys
import csv
import subprocess
import Tkinter as tk
import tkFileDialog as filedialog
import tkMessageBox as confirmDialog
from . import AutoCompleter
from . import PlaceHolderEntry

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
        self.save_route_path = os.path.join(plugin_dir, 'route.csv')
        self.offset_file_path = os.path.join(plugin_dir, 'offset')
        self.offset = 0
        self.jumps_left = 0
        self.error_txt = tk.StringVar()
        self.plot_error = "Error while trying to plot a route, please try again."


    def init_gui(self, parent):
        self.parent = parent
        parentwidth = parent.winfo_width()
        self.frame = tk.Frame(parent, borderwidth=2)
        self.frame.grid(sticky=tk.NSEW)

        # Route info
        self.waypoint_prev_btn = tk.Button(self.frame, text="^", command=self.goto_prev_waypoint)
        self.waypoint_btn = tk.Button(self.frame, text=self.next_wp_label + self.next_stop, command=self.copy_waypoint)
        self.waypoint_next_btn = tk.Button(self.frame, text="v", command=self.goto_next_waypoint)
        self.jumpcounttxt_lbl = tk.Label(self.frame, text=self.jumpcountlbl_txt + str(self.jumps_left))
        self.error_lbl = tk.Label(self.frame, textvariable=self.error_txt)

        # Plotting GUI
        self.source_ac = AutoCompleter(self.frame, "Source System", width=30)
        self.dest_ac = AutoCompleter(self.frame, "Destination System", width=30)
        self.range_entry = PlaceHolderEntry(self.frame, "Range (LY)", width=10)
        self.efficiency_slider = tk.Scale(self.frame, from_=1, to=100, orient=tk.HORIZONTAL, label="Efficiency (%)")
        self.efficiency_slider.set(60)
        self.plot_gui_btn = tk.Button(self.frame, text="Plot route", command=self.show_plot_gui)
        self.plot_route_btn = tk.Button(self.frame, text="Calculate", command=plot_route)
        self.cancel_plot = tk.Button(self.frame, text="Cancel", command=lambda: self.show_plot_gui(False))
        
        self.csv_route_btn = tk.Button(self.frame, text="Import CSV", command=plot_csv)
        self.clear_route_btn = tk.Button(self.frame, text="Clear route", command=clear_route)

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

        show_plot_gui(False)

        if not self.route.__len__() > 0:
            self.waypoint_prev_btn.grid_remove()
            self.waypoint_btn.grid_remove()
            self.waypoint_next_btn.grid_remove()
            self.jumpcounttxt_lbl.grid_remove()
            self.clear_route_btn.grid_remove()

        if self.update_available:
            update_txt = ("A SpanshRouter update is available.\n"
                "It will be installed next time you start EDMC.\n"
                "Click to dismiss this message, right click to see what's new.")
            self.update_btn = tk.Button(self.frame, text=update_txt, command=lambda: self.update_btn.grid_forget())
            self.update_btn.bind("<Button-3>", goto_changelog_page)
            self.update_btn.grid(row=row, pady=5, columnspan=2)
            row += 1

        update_gui()

        return self.frame


    def open_last_route(self):
        try:
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

            for row in self.route[self.offset:]:
                self.jumps_left += int(row[1])

            self.next_stop = self.route[self.offset][0]
            self.copy_waypoint()
        except:
            print("No previously saved route.")

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
            update_route(1)

    def goto_prev_waypoint(self):
        if self.offset > 0:
            update_route(-1)

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
            self.dest_ac.grid()
            self.range_entry.grid()
            self.efficiency_slider.grid()
            self.plot_route_btn.grid()
            self.cancel_plot.grid()

            # Workaround because EDMC keeps switching the placeholder to bright white
            if self.source_ac.get() == self.source_ac.placeholder:
                self.source_ac.force_placeholder_color()
            if self.dest_ac.get() == self.dest_ac.placeholder:
                self.dest_ac.force_placeholder_color()
            if self.range_entry.get() == self.range_entry.placeholder:
                self.range_entry.force_placeholder_color()
            show_route_gui(False)

        else:
            self.source_ac.put_placeholder()
            self.dest_ac.put_placeholder()
            self.source_ac.grid_remove()
            self.dest_ac.grid_remove()
            self.range_entry.grid_remove()
            self.efficiency_slider.grid_remove()
            self.plot_gui_btn.grid_remove()
            self.plot_route_btn.grid_remove()
            self.cancel_plot.grid_remove()
            self.plot_gui_btn.grid()
            self.csv_route_btn.grid()
            show_route_gui(True)


if __name__ == "__main__":
    pass