from json import JSONEncoder
from pathlib import Path
from typing import Union

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


def create_folder(
    path: Union[str, Path], exist_ok: bool = True, parents: bool = True
) -> Path:
    """Create a folder if it does not exists and returns it

    Args:
        path (Union[str, Path]): Path to the folder
        exist_ok (bool, optional): If False raise an error if the folder already exists.
            Defaults to True.
        parents (bool, optional): If True, also creates parent folders.
            Defaults to True.

    Returns:
        Path: Path to the created folder
    """
    if isinstance(path, str):
        path = Path(path)

    path.mkdir(exist_ok=exist_ok, parents=parents)

    return path


class NumpyJSONEncoder(JSONEncoder):
    """JSONEncoder to store python dict or list containing numpy arrays"""

    def default(self, obj):
        """Transform numpy arrays into JSON serializable object such as list
        see : https://docs.python.org/3/library/json.html#json.JSONEncoder.default
        """
        # numpy.ndarray have dtype, astype and tolist attribute and methods that we want
        # to use to convert their element into JSON serializable objects
        if (
            np is not None
            and hasattr(obj, "dtype")
            and hasattr(obj, "astype")
            and hasattr(obj, "tolist")
        ):
            if np.issubdtype(obj.dtype, np.integer):
                return obj.astype(int).tolist()
            elif np.issubdtype(obj.dtype, np.number):
                return obj.astype(float).tolist()
            else:
                return obj.tolist()

        # sets are not json serializable
        elif isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)
