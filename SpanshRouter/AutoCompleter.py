#!/usr/bin/env python2

import threading
import Queue
import json
import os
import requests
import traceback
from Tkinter import *
from time import sleep
from PlaceHolder import PlaceHolder

class AutoCompleter(Entry, PlaceHolder):
    def __init__(self, parent, placeholder, **kw):
        Entry.__init__(self, parent, **kw)
        self.var = self["textvariable"] = StringVar()
        self.var.trace('w', self.changed)

        self.parent = parent

        self.lb = Listbox(self.parent, **kw)
        self.lb_up = False
        self.has_selected = False
        self.queue = Queue.Queue()

        PlaceHolder.__init__(self, placeholder)

        self.bind("<Any-Key>", self.keypressed)
        self.bind('<Control-KeyRelease-a>', self.select_all)
        self.bind('<Button-3>', self.paste)
        self.lb.bind("<Double-Button-1>", self.selection)
        
        self.update_me()

    def paste(self, event):
        self.foc_in()
        self.insert(0, self.clipboard_get())

    def keypressed(self, event):
        key=event.keysym
        if key == 'Down':
            self.down()
        elif key == 'Up':
            self.up()
        elif key in ['Return', 'Right']:
            if self.lb_up:
                self.selection()
        elif key == 'Escape' and self.lb_up:
            self.hide_list()
    
    def select_all(self, event):
        event.widget.event_generate('<<SelectAll>>')

    def changed(self, name, index, mode):
        if self.var.get().__len__() < 3 and self.lb_up or self.has_selected:
            self.hide_list()
            self.has_selected = False
        else:
            t = threading.Thread(target=self.query_systems)
            t.start()
        
    def selection(self, event=None):
        if self.lb_up:
            self.has_selected = True
            self.var.set(self.lb.get(ACTIVE))
            self.hide_list()
            self.icursor(END)

    def up(self):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':                
                self.lb.selection_clear(first=index)
                index = str(int(index)-1)                
                self.lb.selection_set(first=index)
                self.lb.activate(index) 

    def down(self):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
                if int(index+1) != END:
                    self.lb.selection_clear(first=index)
                    index = str(int(index+1))
    
            self.lb.selection_set(first=index)
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
                self.lb.grid(row=info["row"]+1, columnspan=2)
                self.lb_up = True

    def hide_list(self):
        if self.lb_up:
            self.lb.grid_remove()
            self.lb_up = False

    def query_systems(self):
        inp = self.var.get()
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
            except NameError:
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
        except Queue.Empty:
            pass
        self.after(100, self.update_me)

if __name__ == '__main__':
    root = Tk()

    widget = AutoCompleter(root, "Test")
    widget.grid(row=0)
    root.mainloop()