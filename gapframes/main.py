"""
Main actions live here.
"""

# gapframes imports
from ui.communicator import COMMUNICATOR
from ui.panel import GapframesPanel

PANEL = None

# TODO: need to implement a way of re-initializing the Panel if fully closed and destroyed
def open_panel():
    global PANEL
    if PANEL is None:
        PANEL = GapframesPanel()
        PANEL._connect_communicator(COMMUNICATOR)
    PANEL.show()

# TODO: swap with open_panel above for regular use
# def open_panel():
#     COMMUNICATOR.show_gapframes_panel()

def cycle_next_gapframe():
    COMMUNICATOR.emit_cycle_next()

def cycle_prev_gapframe():
    COMMUNICATOR.emit_cycle_prev()

def cycle_gap_distance():
    COMMUNICATOR.emit_cycle_gap_distance()
