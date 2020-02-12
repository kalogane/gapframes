"""
Main actions live here.
"""

# gapframes imports
from ui.communicator import COMMUNICATOR
from ui.panel import GapframesPanel

PANEL = None

# TODO: need to implement a way of re-initializing the Panel if fully closed and destroyed.
def _add_keybindings():
    import nuke
    menu = nuke.toolbar("Nuke").menu("Viewer")
    menu.addSeparator()

    menu.addCommand("Gapframes: Cycle Prev", cycle_prev_gapframe, "alt+a", shortcutContext=1)
    menu.addCommand("Gapframes: Cycle Next", cycle_next_gapframe, "alt+d", shortcutContext=1)
    menu.addCommand("Gapframes: Cycle Gap Distance", cycle_gap_distance, "alt+e", shortcutContext=1)
    menu.addCommand("Gapframes: Update Gaps list", update_gap_list, "alt+q", shortcutContext=1)

def open_panel():
    global PANEL
    if PANEL is None:
        PANEL = GapframesPanel()
        PANEL._connect_communicator(COMMUNICATOR)
        _add_keybindings()
    PANEL.show()

# TODO: swap with open_panel above for regular use, add the keybinds here too
# def open_panel():
#     COMMUNICATOR.show_gapframes_panel()

def cycle_next_gapframe():
    COMMUNICATOR.emit_cycle_next()

def cycle_prev_gapframe():
    COMMUNICATOR.emit_cycle_prev()

def cycle_gap_distance():
    COMMUNICATOR.emit_cycle_gap_distance()

def update_gap_list():
    COMMUNICATOR.emit_update_gap_list()
