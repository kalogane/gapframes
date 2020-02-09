from operator import itemgetter

from constants import NUM_TYPES

class GapsContainer(list):
    """
    Modified Python list class containing convenience functionality to store and extract
    information and string representation of keyframe gaps.
    """
    def __init__(self, items=None, repr_padding=4):
        """
        Args:
            items (iterable, optional): initial items to add to the container
            repr_padding (int, optional): an overall padding number for string representation
                                          of keyframe gaps
        """
        self.repr_padding = repr_padding

        if items is None:
            items = []

        new_items = []
        for item in items:
            self._check_item(item)
            # We need to create an entry manually here because we're using the native list append method.
            new_items.append(self.create_entry(item))

        super(GapsContainer, self).__init__(new_items)

    def _check_item(self, item):
        """
        Check that an incoming item is a dictionary with a signature as created by the create_entry function,
        or that it contains valid numbers for start and end of a range.
        """
        if isinstance(item, dict):  # TODO: revisit - move sample_dict in constants.py?
            sample_dict = {"start": NUM_TYPES, "end": NUM_TYPES, "length": NUM_TYPES, "repr": str}

            error_msg = ("Missing keys or invalid values in input dict. "
                         "Please refer to the create_entry docstring for valid signature.")
            for key, valid_types in sample_dict.items():
                assert item.has_key(key) and isinstance(item.get(key), valid_types), error_msg
            return True  # Valid dict entry.

        assert len(item) == 2, "An input of 2 numbers is necessary."
        start = item[0]
        end = item[1]

        error_msg = "Frame numbers should be int/float."
        assert all((isinstance(start, NUM_TYPES), isinstance(end, NUM_TYPES))), error_msg

        assert end > start, "End number should be higher than start number."
        return True # Valid (start, end) entry.

    def create_entry(self, gap):
        """
        Create a dict entry for a frame range gap, containing info about start/end frame,
        length of the range and a string representation of the gap.

        Args:
            gap (tuple): tuple containing start and end number of a number range

        Return:
            dict: dictionary containing info about a gap's start/end numbers, the gap length
                  and a string representation, e.g.:
                  {"start": int/float, "end": int/float, "length": int/float, "repr": str}
        """
        gap_start = gap[0]
        gap_end = gap[1]
        gap_length = gap_end - gap_start

        representation = "{0:0{padding}d} - {1:0{padding}d} ({2} frames)"
        representation = representation.format(gap_start, gap_end, gap_length, padding=self.repr_padding)

        details = {"start": gap_start, "end": gap_end, "length": gap_length, "repr": representation}
        return details

    def append(self, item):
        """
        Overwrite append func to ensure inputs match necessary signature,
        and create an appropriate entry.

        Args:
            item (iterable): an iterable of 2 numbers representing a start and end of a number range
        """
        self._check_item(item)
        if not isinstance(item, dict):
            item = self.create_entry(item)
        super(GapsContainer, self).append(item)

    def sort_chronologically(self):
        """
        Sort the list chronologically, by the stored dict information about the gap's start frame.
        """
        self.sort(key=itemgetter("start"))

    def sort_by_largest_gap(self):
        """
        Sort the list by the largest number stored in each dict's "length" key.
        """
        self.sort(key=itemgetter("length"), reverse=True)

    def sort_by_smallest_gap(self):
        """
        Sort the list by the smallest number stored in each dict's "length" key.
        """
        self.sort(key=itemgetter("length"))
