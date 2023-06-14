"""VIPickle errors.

VIPickle custom errors
"""


class DumpAttributeError(AttributeError):
    """Use to indicate that the dumping method is not implemented."""


class RestoreAttributeError(AttributeError):
    """Use to indicate that the restoring method is not implemented."""
