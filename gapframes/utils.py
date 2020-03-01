import nuke

from constants import NUM_TYPES

from gapframes.ui.communicator import COMMUNICATOR


# ============================================================================================
# Keyframe utils.

def scan_node_for_keyframes(node, allow_knobs=None, exclude_knobs=None,
                                  boundary_in=None, boundary_out=None):
    """
    Args:
        node (Nuke Node): Nuke Node object
        allow_knobs (list, optional): list of specific knobs names which to scan for keyframes
        exclude_knobs (list, optional): list of knobs names which to ignore
                                        when scanning for keyframes
        boundary_in (int, optional): any keyframes on the timeline below this number
            will not be factored when finding the largest gap
        boundary_out (int, optional): any keyframes on the timeline above this number
            will not be factored when finding the largest gap

    Return:
        list: all key frame numbers for the node
    """
    ctrl_panel_open = node.shown()
    if not ctrl_panel_open:
        # This is necessary to be able to see keyframes on knobs.
        nuke.show(node)

    all_knobs = node.knobs()
    if allow_knobs:
        all_knobs = dict([(k, v) for k, v in all_knobs.items() if k in allow_knobs])
    if exclude_knobs:
        all_knobs = dict([(k, v) for k, v in all_knobs.items() if k not in exclude_knobs])

    all_keys = set()
    for knob in all_knobs.values():
        key_list = knob.getKeyList()
        if all(isinstance(obj, NUM_TYPES) for obj in (boundary_in, boundary_out)):
            key_list = [k for k in key_list if boundary_in < k < boundary_out]
        all_keys.update(key_list)

    if not ctrl_panel_open:
        # If node's Properties were closed to be begin with, close them again.
        node.hideControlPanel()

    return sorted(all_keys)

def get_all_key_frame_nums(nodes, allow_knobs=None, exclude_knobs=None,
                                  boundary_in=None, boundary_out=None):
    """
    Find all key frame numbers for each node in nodes.

    Args:
        nodes (list): list of nodes to get all key frames for
        allow_knobs (list, optional): list of specific knobs names which to scan for keyframes
        exclude_knobs (list, optional): list of knobs names which to ignore
                                        when scanning for keyframes
        boundary_in (int, optional): any keyframes on the timeline below this number
            will not be factored when finding the largest gap
        boundary_out (int, optional): any keyframes on the timeline above this number
            will not be factored when finding the largest gap

    Return:
        list: all key frame numbers
    """
    all_keys = set()
    for node in nodes:
        node_keys = scan_node_for_keyframes(node, allow_knobs, exclude_knobs,
                                            boundary_in, boundary_out)
        all_keys.update(node_keys)

    return sorted(all_keys)

def find_all_gaps(nodes, allow_knobs=None, exclude_knobs=None, boundary_in=None, boundary_out=None):
    """
    Given a sorted array of any numbers, find each chronological pair of keyframe numbers.

    Args:
        nodes (list): list of nodes to get all key frames for
        allow_knobs (list, optional): list of specific knobs names which to scan for keyframes
        exclude_knobs (list, optional): list of knobs names which to ignore
                                        when scanning for keyframes
        boundary_in (int, optional): any keyframes on the timeline below this number
            will not be factored when finding the largest gap
        boundary_out (int, optional): any keyframes on the timeline above this number
            will not be factored when finding the largest gap

    Return:
        list: list of tuples, each containing neighbouring numbers
    """
    keyframes = get_all_key_frame_nums(nodes, allow_knobs, exclude_knobs,
                                       boundary_in, boundary_out)
    if len(keyframes) < 2:
        error_msg = "Need input with 2 or more key frames."
        COMMUNICATOR.report_message_with_error(error_msg, error_type=ValueError)

    all_gaps = []
    for x in range(1, len(keyframes)):
        first = keyframes[x-1]
        second = keyframes[x]

        all_gaps.append((first, second))

    return all_gaps

def find_largest_gap(nodes, allow_knobs=None, exclude_knobs=None,
                            boundary_in=None, boundary_out=None):
    """
    Find the keyframe pair which have the biggest difference out of each pair of discovered
    keyframes in the provided nodes.

    Args:
        nodes (list): list of nodes to get all key frames for
        allow_knobs (list, optional): list of specific knobs names which to scan for keyframes
        exclude_knobs (list, optional): list of knobs names which to ignore
                                        when scanning for keyframes
        boundary_in (int, optional): any keyframes on the timeline below this number
            will not be factored when finding the largest gap
        boundary_out (int, optional): any keyframes on the timeline above this number
            will not be factored when finding the largest gap

    Return:
        tuple: keyframes at the beginning and end of the largest gap
    """
    all_gaps = find_all_gaps(nodes, allow_knobs, exclude_knobs, boundary_in, boundary_out)
    
    max_diff = largest_gap = 0
    for start, end in all_gaps:
        diff = end - start
        if diff > max_diff:
            max_diff = diff
            largest_gap = (start, end)

    return largest_gap
