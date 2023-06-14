"""vipckle.save_utils tests."""

from pathlib import Path

import pytest
from vipickle import save_utils


def test_create_folder(tmp_path: Path):
    """Test create_folder function."""
    created_folder = save_utils.create_folder(tmp_path / "a/b/c")
    assert created_folder.is_dir()

    created_folder = save_utils.create_folder(f"{tmp_path}/1/2")
    assert created_folder.is_dir()

    with pytest.raises(FileExistsError):
        created_folder = save_utils.create_folder(tmp_path / "a/b/c", exist_ok=False)

    with pytest.raises(FileNotFoundError):
        created_folder = save_utils.create_folder(tmp_path / "sub/sub", parents=False)
