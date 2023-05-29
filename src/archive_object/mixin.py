import json
import pickle
from pathlib import Path
from typing import Dict, Iterable, Union

from loguru import logger

from .utils import NumpyJSONEncoder


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
        Path: _description_
    """
    if isinstance(path, str):
        path = Path(path)

    path.mkdir(exist_ok=exist_ok, parents=parents)

    return path


class DumpAttributeError(Exception):
    ...


class RestoreAttributeError(Exception):
    ...


class MetaArchivable(type):
    """Metaclass for Archivable

    This metaclass is aimed to be used with Archivable class. It add the functionality
    to inherit attributes from the parent classes. Which is usefull for adding or
    removing attributes from PICKLE_BLACKLIST and CONFIG_ITEMS.
    """

    def __new__(cls, name: str, parents: tuple, attributes: dict):
        """Metaclass constructor for CONFIG_ITEMS and PICKLE_BLACKLIST construction of
        archivables classes

        Args:
            name (str): Name of the class
            parents (tuple): Parent classes
            attributes (dict): Class attributes

        Returns:
            class: a new class
        """
        # We set a default value for CONFIG_NAME if the attribute does not exists
        if not attributes.get("CONFIG_NAME"):
            attributes["CONFIG_NAME"] = "config.json"

        # We set a default value for PICKLE_NAME if the attribute does not exists
        if not attributes.get("PICKLE_NAME"):
            attributes["PICKLE_NAME"] = f"{name.lower()}.pkl"

        for prefix in ("PICKLE", "CONFIG"):
            # If the class has a {prefix}_BLACKLIST attribute, it will be used as it is
            # we convert it to a set to prevent duplicated values
            if f"{prefix}_BLACKLIST" in attributes:
                pickle_blacklist = {key for key in attributes[f"{prefix}_BLACKLIST"]}

            # Otherwise the {prefix}_BLACKLIST attribute will be created from the parent
            # classes {prefix}_BLACKLIST attributes and the {prefix}_BLACKLIST_ADD and
            # {prefix}_BLACKLIST_REMOVE attributes
            else:
                pickle_blacklist = set()

                # First we get the union of all pickle_blacklist of the parents
                for parent in parents:
                    if issubclass(parent, Archivable):
                        pickle_blacklist = pickle_blacklist.union(
                            getattr(parent, f"{prefix}_BLACKLIST", set())
                        )

                # Then we add attributes from {prefix}_BLACKLIST_ADD
                pickle_blacklist = pickle_blacklist.union(
                    attributes.get(f"{prefix}_BLACKLIST_ADD", set())
                )
                # and we remove attributes from {prefix}_BLACKLIST_REMOVE
                pickle_blacklist = pickle_blacklist.difference(
                    attributes.get(f"{prefix}_BLACKLIST_REMOVE", set())
                )

            # Finnaly, {prefix}_BLACKLIST is converted to a tuple for immutablity
            attributes[f"{prefix}_BLACKLIST"] = tuple(sorted(pickle_blacklist))

        return super().__new__(cls, name, parents, attributes)


class Archivable(metaclass=MetaArchivable):
    PICKLE_NAME: str = None
    PICKLE_BLACKLIST: Iterable[str] = ()
    PICKLE_BLACKLIST_ADD: Iterable[str] = ()
    PICKLE_BLACKLIST_REMOVE: Iterable[str] = ()

    CONFIG_NAME: str = None
    CONFIG_ITEMS: Iterable[str] = ()
    CONFIG_ITEMS_ADD: Iterable[str] = ()
    CONFIG_ITEMS_REMOVE: Iterable[str] = ()

    @property
    def configurations(self) -> dict:
        return {
            key: getattr(self, key) for key in self.CONFIG_ITEMS if hasattr(self, key)
        }

    def __getstate__(self):
        """Pickle all attributes except the ones listed in PICKLE_BLACKLIST"""
        return {
            attribute: state
            for attribute, state in self.__dict__.items()
            if attribute not in self.PICKLE_BLACKLIST
        }

    def save(
        self,
        path: Union[str, Path],
        pickle_dump_kwargs: dict = None,
        json_dump_kwargs: dict = None,
    ):
        # Before save hook
        self.before_save()

        path = create_folder(path)

        if pickle_dump_kwargs is None:
            pickle_dump_kwargs = {}

        if json_dump_kwargs is None:
            json_dump_kwargs = {}

        self.save_instance(path, **json_dump_kwargs)
        self.save_config(path, **json_dump_kwargs)
        self.save_pickle_blacklisted(path)

        # After save hook
        self.after_save()

    def before_save(self):
        """Hook executed at the beggining of the save method"""

    def after_save(self):
        """Hook executed at the end of the save method"""

    def save_instance(self, path: Union[str, Path], **kwargs):
        """Save the current instance

        Args:
            path (Union[str, Path]): path to a folder where to save the current instance
        """
        path = create_folder(path)

        with open(path / self.PICKLE_NAME, "wb") as f:
            pickle.dump(self, f, **kwargs)

    def save_config(
        self, path: Union[str, Path], indent: int = 2, cls=NumpyJSONEncoder, **kwargs
    ):
        """Save the instance configuration attributes

        Args:
            path (Union[str, Path]): path to a folder where to save the current instance
                config file
            indent (int, optional): JSON indentation. Defaults to 2.
            cls (_type_, optional): JSON encoder object. Defaults to NumpyJSONEncoder.
        """
        path = create_folder(path)

        with open(path / self.CONFIG_NAME, "w") as f:
            json.dump(self.configurations, f, indent=indent, cls=cls, **kwargs)

    def save_pickle_blacklisted(self, path: Union[str, Path]) -> Dict[Exception]:
        """Try to save excluded attributes

        Args:
            path (Union[str, Path]): path to a folder where to save blacklisted
                attributes
        """
        path = create_folder(path)
        failures = {}

        for attribute in self.PICKLE_BLACKLIST:
            try:
                getattr(self, f"__dump_{attribute}__")(path)
            except AttributeError as e:
                logger.debug(
                    f"self.{attribute} count not be dumped since there is no "
                    f"method {self.__class__.__name__}.__dump_{attribute}__"
                )
                failures[attribute] = e
            except DumpAttributeError as e:
                logger.warning(
                    f"{self.__class__.__name__}.__dump_{attribute}__ failed : "
                    f"self.{attribute} could not be dumped"
                )
                logger.exception(e)
                failures[attribute] = e

        return failures

    @classmethod
    def load_instance(cls, path: Union[str, Path], **kwargs) -> "Archivable":
        """Load a Archivable instance and all loadable attributes from
        a file or folder

        Args:
            path (Union[str, Path]): Path to the pickle file
        Raises:
            FileNotFoundError: Pickle file not found
        Returns:
            Archivable: The instance object
        """
        with open(path, "rb") as f:
            return pickle.load(f, **kwargs)

    @classmethod
    def load(
        cls,
        path: Union[str, Path],
        pickle_dump_kwargs: dict = None,
        json_dump_kwargs: dict = None,
    ) -> "Archivable":
        """Load a Archivable instance and all loadable attributes from
        a file or folder

        Args:
            path (Union[str, Path]): Path to the pickle file
        Raises:
            FileNotFoundError: Pickle file not found
        Returns:
            Archivable: The instance object
        """
        if isinstance(path, str):
            path = Path(path)

        if pickle_dump_kwargs is None:
            pickle_dump_kwargs = {}

        if json_dump_kwargs is None:
            json_dump_kwargs = {}

        if path.is_dir():
            pickle_path = path / cls.PICKLE_NAME
            folder_path = path
        elif path.is_file():
            pickle_path = path
            folder_path = path.parent
        else:
            raise FileNotFoundError(f"{path} not found")

        cls.before_load()

        obj = cls.load_instance(pickle_path, **pickle_dump_kwargs)
        obj.load_pickle_blacklisted(folder_path)

        obj.after_load()
        return obj

    def before_load(self):
        """Hook executed at the beggining of the load method"""

    def after_load(self):
        """Hook executed at the end of the load method"""

    def load_pickle_blacklisted(self, path: Union[str, Path]) -> Dict[Exception]:
        """Try to unpickle excluded attributes"""
        failures = {}
        for attribute in self.PICKLE_BLACKLIST:
            try:
                getattr(self, f"__restore_{attribute}__")(path)
            except AttributeError as e:
                logger.debug(
                    f"self.{attribute} count not be unpickled since there is no "
                    f"method {self.__class__.__name__}.__restore_{attribute}__"
                )
                failures[attribute] = e
            except RestoreAttributeError as e:
                logger.warning(
                    f"{self.__class__.__name__}.__restore_{attribute}__ failed : "
                    f"self.{attribute} could not be restored"
                )
                logger.exception(e)
                failures[attribute] = e

        return failures
