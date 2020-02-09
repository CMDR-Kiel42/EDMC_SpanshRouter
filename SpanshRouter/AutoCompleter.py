import threading
import json
import os
import requests
import traceback
from time import sleep
from SpanshRouter.PlaceHolder import PlaceHolder
import sys

try:
    # Python 2
    from Tkinter import *
    import ttk   
except ModuleNotFoundError:
    # Python 3
    import tkinter as tk
    from tkinter import *
    
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue 
    

class AutoCompleter(Entry, PlaceHolder):
    def __init__(self, parent, placeholder, **kw):
        Entry.__init__(self, parent, **kw)
        self.var = self["textvariable"] = StringVar()
        self.var.traceid = self.var.trace('w', self.changed)

        self.parent = parent

        self.lb = Listbox(self.parent, selectmode=SINGLE, **kw)
        self.lb_up = False
        self.has_selected = False
        self.queue = queue.Queue()

        PlaceHolder.__init__(self, placeholder)

        # Create right click menu
        self.menu = Menu(self.parent, tearoff=0)
        self.menu.add_command(label="Cut")
        self.menu.add_command(label="Copy")
        self.menu.add_command(label="Paste")

        self.bind("<Any-Key>", self.keypressed)
        self.lb.bind("<Any-Key>", self.keypressed)
        self.bind('<Control-KeyRelease-a>', self.select_all)
        self.bind('<Button-3>', self.show_menu)
        self.lb.bind("<Double-Button-1>", self.selection)
        self.bind("<FocusOut>", self.ac_foc_out)
        self.lb.bind("<FocusOut>", self.ac_foc_out)

        self.update_me()

    def ac_foc_out(self, event):
        x,y = self.parent.winfo_pointerxy()
        widget_under_cursor = self.parent.winfo_containing(x,y)
        if widget_under_cursor != self.lb and widget_under_cursor != self:
            self.foc_out()
            self.hide_list()
    
    def show_menu(self, e):
        self.foc_in()
        w = e.widget
        self.menu.entryconfigure("Cut",
        command=lambda: w.event_generate("<<Cut>>"))
        self.menu.entryconfigure("Copy",
        command=lambda: w.event_generate("<<Copy>>"))
        self.menu.entryconfigure("Paste",
        command=lambda: w.event_generate("<<Paste>>"))
        self.menu.tk.call("tk_popup", self.menu, e.x_root, e.y_root)

    def keypressed(self, event):
        key=event.keysym
        if key == 'Down':
            self.down(event.widget.widgetName)
        elif key == 'Up':
            self.up(event.widget.widgetName)
        elif key in ['Return', 'Right']:
            if self.lb_up:
                self.selection()
        elif key == 'Escape' and self.lb_up:
            self.hide_list()
    
    def select_all(self, event):
        event.widget.event_generate('<<SelectAll>>')

    def changed(self, name, index, mode):
        self.set_default_style()
        value = self.var.get()
        if value.__len__() < 3 and self.lb_up or self.has_selected:
            self.hide_list()
            self.has_selected = False
        else:
            t = threading.Thread(target=self.query_systems, args=[value])
            t.start()
        
    def selection(self, event=None):
        if self.lb_up:
            self.has_selected = True
            self.var.set(self.lb.get(ACTIVE))
            self.hide_list()
            self.icursor(END)

    def up(self, widget):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':                
                self.lb.selection_clear(first=index)
                index = str(int(index)-1)                
                self.lb.selection_set(first=index)
                if widget != "listbox":
                    self.lb.activate(index) 

    def down(self, widget):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
                if int(index+1) != END:
                    self.lb.selection_clear(first=index)
                    index = str(int(index+1))
    
            self.lb.selection_set(first=index)
            if widget != "listbox":
                self.lb.activate(index)
        else:
            self.query_systems()

    def show_results(self, results):
        if results:
            self.lb.delete(0, END)
            for w in results:
                self.lb.insert(END,w)

            self.show_list(len(results))
        else:
            if self.lb_up:
                self.hide_list()

    def show_list(self, height):
        self.lb["height"] = height
        if not self.lb_up:
            info = self.grid_info()
            if info:
                self.lb.grid(row=int(info["row"])+1, columnspan=2)
                self.lb_up = True

    def hide_list(self):
        if self.lb_up:
            self.lb.grid_remove()
            self.lb_up = False

    def query_systems(self, inp):
        inp = inp.strip()
        if inp != self.placeholder and inp.__len__() >= 3:
            url = "https://spansh.co.uk/api/systems?"
            try:
                results = requests.get(url, 
                    params={'q': inp}, 
                    headers={'User-Agent': "EDMC_SpanshRouter 1.0"},
                    timeout=3)

                lista = json.loads(results.content)
                if lista:
                    self.write(lista)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                sys.stderr.write(''.join('!! ' + line for line in lines))

    def write(self, lista):
        self.queue.put(lista)
        
    def clear(self):
        self.queue.put(None)

    def update_me(self):
        try:
            while 1:
                lista = self.queue.get_nowait()
                self.show_results(lista)
                self.update_idletasks()
        except queue.Empty:
            pass
        self.after(100, self.update_me)
    
    def set_text(self, text):
        self.var.trace_vdelete("w", self.var.traceid)
        self.set_default_style()
        self.delete(0, END)
        self.insert(0, text)
        self.var.traceid = self.var.trace('w', self.changed)

if __name__ == '__main__':
    root = Tk()

    widget = AutoCompleter(root, "Test")
    widget.grid(row=0)
    root.mainloop()
