import imp
import os

# Find the UI file in the "ui" submodule directory of gapframes.
_, gapframes_path, _ = imp.find_module("gapframes")
PANEL_UI_PATH =  os.path.join(gapframes_path, "ui", "GapframesPanel.ui")

# Do a stat check to make sure file can be accessed, error if not because we need it.
try:
    os.stat(PANEL_UI_PATH)
except OSError:
    raise OSError("UI file necessary for Gapframes was not found. "
                  "Is the tool installed correctly?")

NUM_TYPES = (int, float)
