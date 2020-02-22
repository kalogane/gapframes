"""
Main actions live here.
"""

# gapframes imports
from gapframes.ui.communicator import COMMUNICATOR
from gapframes.ui.panel import GapframesPanel

PANEL = None

# TODO: need to implement a way of re-initializing the Panel if fully closed and destroyed.
def open_panel():
    global PANEL
    if PANEL is None:
        PANEL = GapframesPanel()
        PANEL.connect_communicator(COMMUNICATOR)
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
