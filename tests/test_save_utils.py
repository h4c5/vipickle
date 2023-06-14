import json
from pathlib import Path

import numpy as np
import pytest
from vipickle import save_utils


def test_create_folder(tmp_path: Path):
    """Test create_folder function"""

    created_folder = save_utils.create_folder(tmp_path / "a/b/c")
    assert created_folder.is_dir()

    created_folder = save_utils.create_folder(f"{tmp_path}/1/2")
    assert created_folder.is_dir()

    with pytest.raises(FileExistsError):
        created_folder = save_utils.create_folder(tmp_path / "a/b/c", exist_ok=False)

    with pytest.raises(FileNotFoundError):
        created_folder = save_utils.create_folder(tmp_path / "sub/sub", parents=False)


def test_json_encoder(tmp_path: Path):
    """Test json_encoder function"""

    test_dict = {
        "int": np.array([1, 2, 3]),
        "float": np.array([1 / 3, 2 / 3, 3 / 3]),
        "str": np.array(["1", "2", "3"]),
        "set": {1, 2, 3},
    }

    with open(tmp_path / "np.json", "w") as f:
        json.dump(test_dict, f, cls=save_utils.NumpyJSONEncoder)

    with open(tmp_path / "np.json", "r") as f:
        loaded_dict = json.load(f)

    for key in ("int", "float", "str"):
        assert np.array_equiv(loaded_dict[key], test_dict[key])

    assert sorted(test_dict["set"]) == sorted(test_dict["set"])

    with pytest.raises(TypeError):
        with open(tmp_path / "fail.json", "w") as f:
            json.dump({"fail": lambda x: x}, f, cls=save_utils.NumpyJSONEncoder)
