import json
import pickle
import random
from pathlib import Path

import pytest
from vipickle import mixin


class CustomArchivableA(mixin.Archivable):
    PICKLE_BLACKLIST = ["unpickable", "wont_recover"]

    def __init__(self, param1: int):
        self.param1 = param1
        self.unpickable = lambda x: x * self.param1
        self.wont_recover = "do not dump"

    def _restore_unpickable_(self, path: Path):
        self.unpickable = lambda x: x * self.param1


def test_pickle_CustomArchivableA(tmp_path: Path):
    """Test to save an instance of CustomArchivableA"""
    # Creating a random CustomArchivableA instance
    param1 = random.randint(1, 100)
    a = CustomArchivableA(param1)
    assert a.wont_recover

    # Saving it to a temp folder
    a.save(tmp_path)

    # By default, the instance is saved under tmp_path/customarchivablea.pkl
    a_path = tmp_path / CustomArchivableA.PICKLE_NAME
    a_config_path = tmp_path / CustomArchivableA.CONFIG_NAME

    assert a_config_path.is_file()

    # If we reload only the instance, the unpickable is not here
    with open(a_path, "rb") as f:
        restored_a = pickle.load(f)

    with pytest.raises(AttributeError):
        restored_a.unpickable(10)

    # But if we reload it completly it is reconstructed by _restore_unpickable_
    restored_a = CustomArchivableA.load(tmp_path)
    assert restored_a.unpickable(10) == 10 * param1

    with pytest.raises(AttributeError):
        restored_a.wont_recover

    # load also work with tmp_path/customarchivablea.pkl
    restored_a = CustomArchivableA.load(a_path)
    assert restored_a.unpickable(10) == 10 * param1

    # load also work with tmp_path/customarchivablea.
    with pytest.raises(FileNotFoundError):
        CustomArchivableA.load(tmp_path / "b.pkl")


class CustomArchivableB(CustomArchivableA):
    """Subclass of CustomArchivableA"""

    PICKLE_BLACKLIST_ADD = ["param3"]
    PICKLE_BLACKLIST_REMOVE = ["wont_recover"]

    def __init__(self, param1: int, param2: int, param3: int):
        super(CustomArchivableB, self).__init__(param1)
        self.param2 = param2
        self.param3 = param3
        self.unpickable = lambda x: self.param1 * self.param2

    def _restore_unpickable_(self, path: Path):
        self.unpickable = lambda x: self.param1 * self.param2


def test_pickle_CustomArchivableB(tmp_path: Path):
    # Creating a random CustomArchivableA instance
    param1 = random.randint(1, 100)
    param2 = random.randint(1, 100)
    param3 = random.randint(1, 100)
    b = CustomArchivableB(param1, param2, param3)
    assert b.wont_recover
    assert b.param1 == param1
    assert b.param2 == param2
    assert b.param3 == param3

    # Saving it to a temp folder
    b.save(tmp_path)

    # We reload it with CustomArchivableA load function, it will work since it is
    # calling load_instance, load_config and load_pickle_blacklisted internally
    restored_b = CustomArchivableA.load(tmp_path)

    assert restored_b.unpickable(10) == param1 * param2
    assert restored_b.wont_recover

    with pytest.raises(AttributeError):
        restored_b.param3


class CustomArchivableC(CustomArchivableB):
    """Subclass of CustomArchivableA"""

    PICKLE_NAME = None
    CONFIG_NAME = ""
    PICKLE_BLACKLIST_ADD = ["wont_recover"]

    def _dump_wont_recover_(self, path: Path, overwrite: bool = False):
        with open(path / "wont_recover.json", "w") as f:
            json.dump({"wont_recover": "or maybe not"}, f)


def test_pickle_CustomArchivableC(tmp_path: Path):
    c = CustomArchivableC(1, 2, 3)
    c.save(tmp_path)

    assert not list(tmp_path.glob("*.pkl"))
    assert (tmp_path / "wont_recover.json").exists()
