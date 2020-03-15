"""
Main actions live here.
"""
from PySide2.QtWidgets import QApplication

# gapframes imports
from gapframes.constants import PANEL_OBJECT_NAME
from gapframes.ui.communicator import COMMUNICATOR
from gapframes.ui.panel import GapframesPanel


def _initialize_panel():
    panel = GapframesPanel()
    panel.connect_communicator(COMMUNICATOR)

_initialize_panel()

def open_panel():
    active_widgets = [w.objectName() for w in QApplication.instance().allWidgets()]
    if PANEL_OBJECT_NAME not in active_widgets:
        # If panel was somehow destroyed, re-initialize it.
        _initialize_panel()
    COMMUNICATOR.show_gapframes_panel()

def cycle_next_gapframe():
    COMMUNICATOR.emit_cycle_next()

def cycle_prev_gapframe():
    COMMUNICATOR.emit_cycle_prev()

def cycle_gap_distance():
    COMMUNICATOR.emit_cycle_gap_distance()

def update_gap_list():
    COMMUNICATOR.emit_update_gap_list()
