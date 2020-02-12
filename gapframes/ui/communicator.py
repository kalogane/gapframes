"""
The Communicator is a "middle man" class, used to communicate with
the necessary parts of the active Gapframes Panel.
Primarily used to safely attach some of the panel functionalities
to Nuke hotkeys.
"""

from PySide2 import QtCore

class Communicator(QtCore.QObject):
    fetch_panel = QtCore.Signal()
    update_gap_list = QtCore.Signal()
    cycle_next = QtCore.Signal()
    cycle_prev = QtCore.Signal()
    cycle_gap_distance = QtCore.Signal()
    relay_message = QtCore.Signal(str, dict)

    def show_gapframes_panel(self):
        self.fetch_panel.emit()

    def emit_cycle_next(self):
        self.cycle_next.emit()

    def emit_cycle_prev(self):
        self.cycle_prev.emit()

    def emit_cycle_gap_distance(self):
        self.cycle_gap_distance.emit()

    def emit_update_gap_list(self):
        self.update_gap_list.emit()

    def report_message(self, msg, in_shell=True, in_nuke=True):
        kwargs = {"in_shell": in_shell, "in_nuke": in_nuke}
        self.relay_message.emit(msg, kwargs)

    def report_message_with_error(self, msg, in_shell=True, in_nuke=True,
                                             error_type=None):
        try:
            raise error_type(msg)
        except error_type:
            self.report_message(msg, in_shell=in_shell, in_nuke=in_nuke)
            raise

COMMUNICATOR = Communicator()
