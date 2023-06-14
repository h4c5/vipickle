"""Saving utilities module.

Module containing utilities functions for saving purpose.
"""
from pathlib import Path
from typing import Union


def create_folder(
    path: Union[str, Path], exist_ok: bool = True, parents: bool = True
) -> Path:
    """Create a folder if it does not exists and returns it.

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
