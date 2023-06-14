"""VIPickle.

VIPickle make any object picklable by specifying which attribute to blacklist when
pickling and how to dump and recover them.
"""

from .errors import DumpAttributeError, RestoreAttributeError
from .mixin import MetaVIPicklable, VIPicklable
from .save_utils import create_folder

__all__ = [
    "DumpAttributeError",
    "RestoreAttributeError",
    "VIPicklable",
    "MetaVIPicklable",
    "create_folder",
]
