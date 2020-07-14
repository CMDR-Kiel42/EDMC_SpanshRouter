import sys
import SpanshRouter.updater as updater
from SpanshRouter.SpanshRouter import SpanshRouter

spansh_router = None
sp_updater = None

def plugin_start3(plugin_dir):
    return plugin_start(plugin_dir)

def plugin_start(plugin_dir):
    global spansh_router
    global sp_updater
    spansh_router = SpanshRouter(plugin_dir)
    sp_updater = updater.SpanshUpdater(plugin_dir)
    return 'spansh_router'

def plugin_stop():
    global spansh_router
    global sp_updater
    spansh_router.save_route()

    if sp_updater.update_available:
        sp_updater.install()

def journal_entry(cmdr, is_beta, system, station, entry, state):
    global spansh_router
    if (entry['event'] in ['FSDJump', 'Location', 'SupercruiseEntry', 'SupercruiseExit']) and entry["StarSystem"] == spansh_router.next_stop:
        spansh_router.update_route()
        spansh_router.set_source_ac(entry["StarSystem"])
    elif entry['event'] == 'FSSDiscoveryScan' and entry['SystemName'] == spansh_router.next_stop:
        spansh_router.update_route()

def ask_for_update():
    global sp_updater
    sp_updater.check_for_update()
    if sp_updater.update_available:
        sp_updater.ask_for_update()

def plugin_app(parent):
    global spansh_router
    spansh_router.init_gui(parent)
    spansh_router.open_last_route()
    parent.master.after_idle(ask_for_update)
