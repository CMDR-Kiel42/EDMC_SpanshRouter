from SpanshRouter import SpanshRouter

spansh_router = None

def plugin_start3(plugin_dir):
    return plugin_start()

def plugin_start():
    # Check for newer versions
    global spansh_router
    spansh_router = SpanshRouter(plugin_dir)
    spansh_router.check_for_update()
    spansh_router.open_last_route()
    return 'spansh_router'

def plugin_stop():
    global spansh_router
    spansh_router.save_route()

    if spansh_router.update_available:
        spansh_router.install_update()

def journal_entry(cmdr, is_beta, system, station, entry, state):
    global spansh_router
    if (entry['event'] in ['FSDJump', 'Location', 'SupercruiseEntry', 'SupercruiseExit']) and entry["StarSystem"] == spansh_router.next_stop:
        spansh_router.update_route()
        spansh_router.set_source_ac(entry["StarSystem"])
    elif entry['event'] == 'FSSDiscoveryScan' and entry['SystemName'] == spansh_router.next_stop:
        spansh_router.update_route()

def plugin_app(parent):
    global spansh_router
    spansh_router.init_gui(parent)