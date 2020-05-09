try:
    # Python 2
    from Tkinter import *
    from .PlaceHolder import PlaceHolder
except ModuleNotFoundError:
    # Python 3
    import tkinter as tk
    from tkinter import *
    from SpanshRouter.PlaceHolder import PlaceHolder

class PlaceHolderEntry(Entry, PlaceHolder):
    def __init__(self, parent, placeholder, **kw):
        Entry.__init__(self, parent, **kw)
        self.var = self["textvariable"] = StringVar()
        PlaceHolder.__init__(self, placeholder)
