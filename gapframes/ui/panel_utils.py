import inspect
import re
from PySide2 import QtWidgets

import nuke

from communicator import COMMUNICATOR
from gapframes.constants import NODE_SELECTION_RADIO_BUTTONS


def _clean_input(input_text):
    """
    Clean up the user input and double check the input sanitization.
    """
    input_items = input_text.replace(" ", "").split(",")
    pattern = r"^[\d\w_]*$" # Only allow nums, letters and underscores.
    sanitized = re.match(pattern, "".join(input_items))

    if not sanitized:
        error_msg = "Illegal characters provided in node/knob names."
        COMMUNICATOR.report_message_with_error(error_msg, error_type=ValueError)

    return input_items

def get_ui_item_names(ui_obj):
    """
    Find all UI item names that follow this naming convention:
    "uiSection_purpose_qtObjectTypeHint(_optionalNumber)"

    Args:
        ui_obj (QObject): the loaded UI file instance

    Returns:
        list: list of strings of UI items
    """
    # The pattern will match the naming convention of the Qt items.
    alphanum_ptn = r"[a-zA-Z0-9]" # Alphanumerical match
    re_ptn = r"^({0}+)_({0}+)_({0}+)_?({0}*)$".format(alphanum_ptn)
    return [n for n,_ in inspect.getmembers(ui_obj) if re.match(re_ptn, n) and not n.startswith("__")]

# Node targeting funcs.
def get_selected_nodes(*args):
    selection = nuke.selectedNodes()
    if not selection:
        msg = "Please select node(s)."
        COMMUNICATOR.report_message_with_error(msg, error_type=ValueError)
    for node in selection:
        # Recurse groups to find all child nodes.
        if node.Class() == "Group":
            nodes_in_group = nuke.allNodes(group=node, recurseGroups=True)
            selection.extend(nodes_in_group)
    return selection

def get_nodes_in_properties_bin(*args):
    nodes = [n for n in nuke.allNodes(recurseGroups=True) if n.shown()]
    if not nodes:
        msg = "No nodes' Properties are currently open."
        COMMUNICATOR.report_message_with_error(msg, error_type=ValueError)

    return nodes

def get_specific_nodes(node_names, *args):
    nodes = []
    for name in node_names:
        node = nuke.toNode(name)
        if node:
            nodes.append(node)
    return nodes

# ==============================================================================================================================
# UI-oriented

def determine_get_nodes_func(ui):
    """
    Determine which function to use to retrieve the nodes which we should scan for keyframes.

    Args:
        ui (QMainWindow): loaded UI instance

    Returns:
        func: function to use to retrieve nodes
        or
        NoneType: if no function was matched to the corresponding radio button option
    """
    nodes_func_map = {
        "nodeSection_propertiesPanel_radioButton": get_nodes_in_properties_bin,
        "nodeSection_selectedNodes_radioButton": get_selected_nodes,
        "nodeSection_specificNodes_radioButton": get_specific_nodes
    }

    button_name = ""
    for button_name in NODE_SELECTION_RADIO_BUTTONS:
        button = ui.findChild(QtWidgets.QRadioButton, button_name)
        if not button:
            continue
        elif button.isChecked():
            # Found which button is checked.
            break

    get_nodes_func = nodes_func_map.get(button_name)
    if not callable(get_nodes_func):
        msg = "Failed to retrieve relevant function for button '{0}'."
        COMMUNICATOR.report_message(msg.format(button_name))
    
    return get_nodes_func

def get_scan_parameters(ui):
    """
    Find various parameters in the UI related to scanning for existing Keyframes.

    Args:
        ui (QMainWindow): loaded UI instance

    Returns: collection of user-specified information in the UI, containing:
             list of nodes, list of allowed knob names, list of knobs names to exclude,
             scan boundary start, scan boundary end
        Example:
        tuple: (list, list, list, int, int)
        or
        tuple: (list, list, list, NoneType, NoneType) if UI boundary setting is 0
    """
    get_nodes_func = determine_get_nodes_func(ui)
    specified_nodes = ui.nodeNames_input_lineEdit.text()
    specified_nodes = _clean_input(specified_nodes) if specified_nodes else []
    # If specified_nodes is irrelevant to the get_nodes_func, they get ignored anyway.
    nodes = get_nodes_func(specified_nodes)

    allow_knobs = ui.knobSection_allowedKnobs_lineEdit.text()
    exclude_knobs = ui.knobSection_excludedKnobs_lineEdit.text()
    # If field left empty, use None.
    allow_knobs = _clean_input(allow_knobs.text()) if allow_knobs else None
    exclude_knobs = _clean_input(exclude_knobs.text()) if exclude_knobs else None

    cur_frame = nuke.frame()
    boundary_value = ui.extraOptions_scanBoundary_spinBox.value()
    boundary_in = boundary_out = None
    if boundary_value is not 0:
        boundary_in = cur_frame - boundary_value
        boundary_out = cur_frame + boundary_value

    return nodes, allow_knobs, exclude_knobs, boundary_in, boundary_out
