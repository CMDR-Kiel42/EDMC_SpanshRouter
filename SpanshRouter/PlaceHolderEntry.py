from SpanshRouter.PlaceHolder import PlaceHolder

try:
    # Python 2
    from Tkinter import *
except ModuleNotFoundError:
    # Python 3
    import tkinter as tk
    from tkinter import *

class PlaceHolderEntry(Entry, PlaceHolder):
    def __init__(self, parent, placeholder, **kw):
        Entry.__init__(self, parent, **kw)
        self.var = self["textvariable"] = StringVar()
        PlaceHolder.__init__(self, placeholder)
