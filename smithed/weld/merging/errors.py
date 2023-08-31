from ..errors import WeldError


class MergingError(WeldError):
    """Error resulting from the merging process"""


class PriorityError(MergingError):
    """Error related to resolving priorities"""
