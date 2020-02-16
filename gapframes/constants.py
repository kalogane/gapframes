import imp
import os

# Find the UI file in the "ui" submodule directory of gapframes.
_, gapframes_path, _ = imp.find_module("gapframes")
PANEL_UI_PATH = os.path.join(gapframes_path, "ui", "GapframesPanel.ui")

NUM_TYPES = (int, float)

# Hotkeys
OPEN_PANEL = "Open Panel"
UPDATE_GAPS_LIST = "Update Gaps list"
CYCLE_GAP_DISTANCE = "Cycle Gap Distance"
CYCLE_PREV = "Cycle Previous"
CYCLE_NEXT = "Cycle Next"

BUTTON_ORDER = [OPEN_PANEL, UPDATE_GAPS_LIST, CYCLE_GAP_DISTANCE, CYCLE_NEXT, CYCLE_PREV]
# "func" has to be the name of a method defined in the Communicator class
HOTKEYS = {
    # "hotkey" here is only the default, actual value is grabbed from UI
    OPEN_PANEL: {"hotkey": "alt+q", "func": "show_gapframes_panel", "ui_elem": "hotkeys_openPanel_lineEdit"},
    UPDATE_GAPS_LIST: {"hotkey": "alt+r", "func": "emit_update_gap_list", "ui_elem": "hotkeys_updateList_lineEdit"},
    CYCLE_GAP_DISTANCE: {"hotkey": "alt+e", "func": "emit_cycle_gap_distance",
                         "ui_elem": "hotkeys_cycleGapDistances_lineEdit"},
    CYCLE_NEXT: {"hotkey": "alt+d", "func": "emit_cycle_next", "ui_elem": "hotkeys_cycleNextItem_lineEdit"},
    CYCLE_PREV: {"hotkey": "alt+a", "func": "emit_cycle_prev", "ui_elem": "hotkeys_cyclePrevItem_lineEdit"}
}
