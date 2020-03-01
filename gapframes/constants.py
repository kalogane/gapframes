import imp
import os

# Find the UI file in the "ui" submodule directory of gapframes.
_, gapframes_path, _ = imp.find_module("gapframes")
PANEL_UI_PATH = os.path.join(gapframes_path, "ui", "GapframesPanel.ui")
PREFERENCES_PATH = os.path.expanduser("~/.nuke/gapframes_preferences.ini")

NUM_TYPES = (int, float)
NODE_SELECTION_RADIO_BUTTONS = ["nodeSection_propertiesPanel_radioButton",
                                "nodeSection_selectedNodes_radioButton",
                                "nodeSection_specificNodes_radioButton"]
# Preferences only need to be restored for the following objects.
PREFERENCES_TARGETS = set(["GapframesPanel", "nodeSection_propertiesPanel_radioButton",
                           "nodeSection_selectedNodes_radioButton", "nodeSection_specificNodes_radioButton",
                           "nodeNames_input_lineEdit", "knobSection_allowedKnobs_lineEdit",
                           "knobSection_excludedKnobs_lineEdit", "hotkeys_openPanel_lineEdit",
                           "hotkeys_updateList_lineEdit", "hotkeys_cycleGapDistances_lineEdit",
                           "hotkeys_cycleNextItem_lineEdit", "hotkeys_cyclePrevItem_lineEdit"])

# Menu item names
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
HOTKEY_UI_ITEMS = [hotkey_settings.get("ui_elem") for hotkey_settings in HOTKEYS.values()]
