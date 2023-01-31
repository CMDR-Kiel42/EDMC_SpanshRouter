import sys
from SpanshRouter.SpanshRouter import SpanshRouter
import tkinter.messagebox as confirmDialog
from typing import Optional
import tkinter as tk


spansh_router = None
IFFSQR: Optional[tk.Frame] = None

def plugin_start3(plugin_dir):
    return plugin_start(plugin_dir)

def plugin_start(plugin_dir):
    global spansh_router
    spansh_router = SpanshRouter(plugin_dir)
    spansh_router.check_for_update()
    return 'spansh_router'

def plugin_stop():
    global spansh_router
    spansh_router.save_route()

    if spansh_router.update_available:
        spansh_router.install_update()

def journal_entry(cmdr, is_beta, system, station, entry, state):
    global spansh_router
    if (    entry['event'] in ['FSDJump', 'Location', 'SupercruiseEntry', 'SupercruiseExit'] 
            and entry["StarSystem"].lower() == spansh_router.next_stop.lower()):
        spansh_router.update_route()
        spansh_router.set_source_ac(entry["StarSystem"])
    elif entry['event'] == 'FSSDiscoveryScan' and entry['SystemName'] == spansh_router.next_stop:
        spansh_router.update_route()

def ask_for_update():
    global spansh_router
    if spansh_router.update_available:
        update_txt = "New Spansh Router update available!\n"
        update_txt += "If you choose to install it, you will have to restart EDMC for it to take effect.\n\n"
        update_txt += spansh_router.spansh_updater.changelogs
        update_txt += "\n\nInstall?"
        install_update = confirmDialog.askyesno("SpanshRouter", update_txt)

        if install_update:
            confirmDialog.showinfo("SpanshRouter", "The update will be installed as soon as you quit EDMC.")
        else:
            spansh_router.update_available = False

def plugin_app(parent: tk.Frame) -> tk.Frame:
    global spansh_router
    global IFFSQR
    IFFSQR = tk.Frame(parent, borderwidth=2)
    spansh_router.init_gui(parent,IFFSQR)
    spansh_router.open_last_route()
    parent.master.after_idle(ask_for_update)
    
    return IFFSQR
