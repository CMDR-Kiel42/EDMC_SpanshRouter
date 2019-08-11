from config import config
from Tkinter import END

class PlaceHolder():
    def __init__(self, placeholder, **kw):
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_fg_color = config.get('dark_text')

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self['fg'] = self.placeholder_color
        if self.get() != self.placeholder:
            self.delete(0, END)
            self.insert(0, self.placeholder)

    def force_placeholder_color(self):
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == "red" or self['fg'] == self.placeholder_color:
            self['fg'] = self.default_fg_color
            if self.get() == self.placeholder:
                self.delete('0', 'end')

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
