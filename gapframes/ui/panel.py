import os
import traceback
from datetime import datetime
from operator import itemgetter

import nuke
from PySide2 import QtCore, QtGui, QtUiTools, QtWidgets

# Gapframes imports
import panel_utils as pu
from gapframes import utils
from gapframes.constants import BUTTON_ORDER, HOTKEYS, PANEL_UI_PATH
from gapframes.gaps_container import GapsContainer
from gapframes.ui.communicator import COMMUNICATOR


class GapframesPanel(QtWidgets.QMainWindow):
    """
    Custom panel for various settings to control the behaviour of the tool.
    """
    def __init__(self, parent=None):
        super(GapframesPanel, self).__init__(parent)
        self._gaps_container = GapsContainer()
        # Save a reference of which hotkeys were last set - {menu_button_name: hotkey}
        self.hotkeys = {}
        self._init_ui()

    def _toggle_window_stays_on_top(self, force_state=None):
        """
        Toggle whether the window should stay on top.
        Input is optional, but can be forced to True or False.
        """
        cur_flags = self.ui.windowFlags()
        stay_on_top_hint = QtCore.Qt.WindowStaysOnTopHint
        set_hint = (cur_flags | stay_on_top_hint)
        remove_hint = (cur_flags & ~stay_on_top_hint)

        # Check current state and set new flags to opposite state, or the forced state.
        cur_state = bool(cur_flags & stay_on_top_hint)
        new_state = force_state if isinstance(force_state, bool) else not cur_state
        new_flags = set_hint if new_state is True else remove_hint

        self.ui.setWindowFlags(new_flags)
        self.ui.show()

    def _add_keybindings(self, on_ui_init=False):
        menu = nuke.toolbar("Nuke").menu("Viewer")
        menu.addSeparator()

        for button_name in BUTTON_ORDER:
            settings = HOTKEYS.get(button_name)
            if not settings:
                continue

            default_hotkey = settings.get("hotkey", "")
            func = getattr(COMMUNICATOR, settings.get("func", ""))
            ui_elem = getattr(self.ui, settings.get("ui_elem", ""))

            new_hotkey = ui_elem.text()
            # TODO: may not want to force default_hotkey on_ui_init after preferences are implemented
            hotkey = (new_hotkey or default_hotkey) if on_ui_init else new_hotkey
            if hotkey == self.hotkeys.get(button_name):
                # If hotkey is the same, do nothing.
                continue

            menu_button_name = "Gapframes: "+button_name
            menu_item = menu.findItem(menu_button_name)
            if menu_item:
                menu_item.setShortcut(hotkey)
            else:
                menu.addCommand(menu_button_name, func, hotkey, shortcutContext=1)

            self.hotkeys[button_name] = hotkey
            ui_elem.setText(hotkey)

    def _init_ui(self):
        # Do a stat check to make sure the UI file can be accessed, error if not because we need it.
        try:
            os.stat(PANEL_UI_PATH)
        except OSError:
            msg = "UI file necessary for Gapframes was not found. Is the tool installed correctly?"
            COMMUNICATOR.report_message_with_error(msg, error_type=OSError)

        self.ui = QtUiTools.QUiLoader().load(PANEL_UI_PATH, self)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self._toggle_window_stays_on_top(True)
        self._setup_input_sanitization()
        self._add_keybindings(on_ui_init=True)
        self._pass_connections()
        self.update_ui()

    def _setup_input_sanitization(self):
        node_knob_input_objects = (
            self.ui.nodeNames_input_lineEdit,
            self.ui.knobSection_allowedKnobs_lineEdit,
            self.ui.knobSection_excludedKnobs_lineEdit
        )
        hotkey_input_objects = (
            self.ui.hotkeys_openPanel_lineEdit,
            self.ui.hotkeys_updateList_lineEdit,
            self.ui.hotkeys_cycleGapDistances_lineEdit,
            self.ui.hotkeys_cycleNextItem_lineEdit,
            self.ui.hotkeys_cyclePrevItem_lineEdit
        )

        # Only allow nums, letters, underscores, commas and spaces.
        node_knob_regex = QtCore.QRegExp(r"[\d\w_, ]*")
        node_knob_validator = QtGui.QRegExpValidator(node_knob_regex, self)
        for obj in node_knob_input_objects:
            obj.setValidator(node_knob_validator)
            # inputRejected signal missing, but is in PySide2 docs??
            # obj.inputRejected.connect(_rejection_message)

        # Only allow nums, letters, +, ^, # - for Nuke hotkeys.
        hotkey_regex = QtCore.QRegExp(r"[\d\w+#^]*")
        hotkey_validator = QtGui.QRegExpValidator(hotkey_regex, self)
        for obj in hotkey_input_objects:
            obj.setValidator(hotkey_validator)

    def _pass_connections(self):
        """
        Connect UI signals to functions.
        """
        ui = self.ui
        ui.bottom_closeWin_pushButton.clicked.connect(self.hide)
        ui.gapsList_update_pushButton.clicked.connect(self.repopulate_gaps_list)
        ui.gapsList_cycleNext_pushButton.clicked.connect(self.cycle_next_item)
        ui.gapsList_cyclePrev_pushButton.clicked.connect(self.cycle_previous_item)
        ui.bottom_jumpAction_pushButton.clicked.connect(self.jump_to_gapframe)
        ui.nodeSection_specificNodes_radioButton.toggled.connect(
            lambda state: self.enable_node_names_field(state)
        )

        for obj in (ui.extraOptions_gapDistance_spinBox, ui.extraOptions_gapDistance_slider):
            obj.valueChanged.connect(lambda val: self._gap_distance_updater(val))

        ui.gapsList_sorting_comboBox.currentIndexChanged.connect(self.sorting_handler)
        ui.gapsList_list_listWidget.currentRowChanged.connect(self.update_cur_gapframe)
        ui.gapsList_list_listWidget.itemDoubleClicked.connect(self.jump_to_gapframe)

        hotkey_ui_items = [hotkey_settings.get("ui_elem") for hotkey_settings in HOTKEYS.values()]
        for item in hotkey_ui_items:
            ui_elem = getattr(self.ui, item)
            ui_elem.editingFinished.connect(self._add_keybindings)

    def _gap_distance_updater(self, value):
        """
        Handle changes to UI elements related to Gap Distance settings.

        Args:
            value (int): the new value when one of the Gap Distance elements are changed
        """
        num_field = self.ui.extraOptions_gapDistance_spinBox
        slider = self.ui.extraOptions_gapDistance_slider

        num_field.blockSignals(True)
        slider.blockSignals(True)

        num_field.setValue(value)
        slider.setValue(value)
        self.update_cur_gapframe()

        num_field.blockSignals(False)
        slider.blockSignals(False)

    def _update_gaps_listWidget(self):
        """
        Clear the Gaps List widget and re-fill with stored gaps information.
        """
        list_widget = self.ui.gapsList_list_listWidget
        list_widget.clear()

        for gap in self._gaps_container:
            item_str = gap.get("repr")
            list_widget.addItem(item_str)

        if len(self._gaps_container) > 0:
            cur_frame = nuke.frame()

            ind = 0 # Fallback default.
            for ind, gap in enumerate(self._gaps_container):
                gap_start = gap.get("start")
                gap_end = gap.get("end")
                if gap_start <= cur_frame <= gap_end:
                    # Found the gap where current Viewer frame is.
                    break

            # Check if current frame is outside of known Keyframe gaps.
            lowest_known = min(self._gaps_container, key=itemgetter("start"))
            highest_known = max(self._gaps_container, key=itemgetter("end"))
            if cur_frame <= lowest_known.get("start"):
                ind = self._gaps_container.index(lowest_known)
            elif cur_frame >= highest_known.get("end"):
                ind = self._gaps_container.index(highest_known)

            list_widget.setCurrentRow(ind)

    def _cycle_gap_distance_value(self):
        """
        Cycle between each quarter of 100% on the Gap Distance slider.
        """
        gap_distance_spinbox = self.ui.extraOptions_gapDistance_spinBox
        gap_distance = gap_distance_spinbox.value()
        set_points = (0, 25, 50, 75, 100)

        if gap_distance not in set_points:
            # Get the closest set point of distance to what the cur setting is.
            new_distance = min(set_points, key=lambda x: abs(x - gap_distance))
        else:
            # Get the next index
            cur_ind = set_points.index(gap_distance)
            new_ind = 0
            if cur_ind < len(set_points)-1:
                new_ind = cur_ind + 1
            new_distance = set_points[new_ind]

        gap_distance_spinbox.setValue(new_distance)

    def show(self):
        self.ui.show()

    def hide(self):
        self.ui.hide()

    def connect_communicator(self, comm):
        """
        Connect external signalling for communication with the Panel.

        Args:
            comm (Communicator obj): the Communicator class from communicator.py
        """
        try:
            comm.fetch_panel.connect(self.show)
            comm.update_gap_list.connect(self.repopulate_gaps_list)
            comm.relay_message.connect(lambda msg, kwargs: self.report_message(msg, **kwargs))
            comm.cycle_next.connect(self.cycle_next_item)
            comm.cycle_prev.connect(self.cycle_previous_item)
            comm.cycle_gap_distance.connect(self._cycle_gap_distance_value)
        except AttributeError:
            self.report_message(traceback.format_exc())

    # TODO: Is this func necessary? Does anything need "updating", either at startup or otherwise?
    # Maybe refactor to be used for "auto update" checkbox.
    def update_ui(self):
        # self.repopulate_gaps_list()
        pass

    def report_message(self, msg, in_shell=True, in_nuke=True):
        print("{0}: {1}".format(self.ui.windowTitle(), msg))
        if in_shell:
            if not isinstance(msg, basestring):
                msg = "{0}".format(msg)
            timestamp = datetime.now().strftime("%d/%m %H:%M")
            shell_msg = "{0} ({1}): {2}".format(self.ui.windowTitle(), timestamp, msg)
            nuke.tprint(shell_msg)
        if in_nuke:
            self.hide()
            nuke.message(msg)
            self.show()

    def repopulate_gaps_list(self, update_container=True, do_sort=True):
        """
        Args:
            update_container (bool, optional): whether to update the internal container with info
                                               about the currently known keyframe gaps
            do_sort (bool, optional): whether to update the sorting of the items in the internal container
        """
        if update_container:
            nodes, allow_knobs, exclude_knobs, boundary_in, boundary_out = \
                pu.get_scan_parameters(self.ui)
            all_gaps = utils.find_all_gaps(nodes, allow_knobs, exclude_knobs,
                                           boundary_in, boundary_out)
            self._gaps_container = GapsContainer(all_gaps) # Replace container.

        if do_sort:
            self.sorting_handler()

        self._update_gaps_listWidget()

    def sorting_handler(self):
        # Would be better if we map names of items instead of indices.
        index_to_func_mapping = {
            0: self._gaps_container.sort_chronologically,
            1: self._gaps_container.sort_by_largest_gap,
            2: self._gaps_container.sort_by_smallest_gap
        }

        cur_index = self.ui.gapsList_sorting_comboBox.currentIndex()
        sorting_func = index_to_func_mapping.get(cur_index, lambda: None)
        sorting_func() # Sort the gaps container in place.

        self.repopulate_gaps_list(update_container=False, do_sort=False)

    def enable_node_names_field(self, state=True):
        """
        Enable or disable the UI elements related to Node Names manual input.

        Args:
            state (bool, optional): whether to enable or disable elements, default: True
        """
        self.ui.nodeNames_input_label.setEnabled(state)
        self.ui.nodeNames_input_lineEdit.setEnabled(state)

    def cycle_next_item(self):
        list_widget = self.ui.gapsList_list_listWidget
        item_count = list_widget.count()
        next_row = list_widget.currentRow()+1

        if next_row >= item_count:
            next_row = 0

        list_widget.setCurrentRow(next_row)
        self.jump_to_gapframe()

    def cycle_previous_item(self):
        list_widget = self.ui.gapsList_list_listWidget
        item_count = list_widget.count()
        prev_row = list_widget.currentRow()-1

        if prev_row < 0:
            prev_row = item_count-1

        list_widget.setCurrentRow(prev_row)
        self.jump_to_gapframe()

    def update_cur_gapframe(self):
        """
        Update what the UI currently considers the "Gapframe".
        """
        list_widget = self.ui.gapsList_list_listWidget
        gapframe_field = self.ui.bottom_curGapframe_spinBox
        cur_row = list_widget.currentRow()

        try:
            cur_gap = self._gaps_container[cur_row]
            gap_start = cur_gap.get("start")
            gap_length = cur_gap.get("length")

            # Take % input from the "Gap Distance" field into account and find the corresponding frame
            # in the currently selected gap entry.
            gap_distance = self.ui.extraOptions_gapDistance_spinBox.value()
            cur_gapframe = gap_start + ((gap_distance * gap_length) / 100.0)
        except:
            # In case of any errors with UI fields or items missing, fall back to 0.
            cur_gapframe = 0
        gapframe_field.setValue(cur_gapframe)

    def jump_to_gapframe(self):
        cur_gapframe = self.ui.bottom_curGapframe_spinBox.value()
        nuke.frame(cur_gapframe)
