#!/usr/bin/env python2

from Tkinter import *
from PlaceHolder import PlaceHolder

class PlaceHolderEntry(Entry, PlaceHolder):
    def __init__(self, parent, placeholder, **kw):
        Entry.__init__(self, parent, **kw)
        PlaceHolder.__init__(self, placeholder)