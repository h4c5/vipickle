import json
import pickle
from pathlib import Path
from typing import Dict, Iterable, Union

from loguru import logger

from .errors import DumpAttributeError, RestoreAttributeError
from .save_utils import NumpyJSONEncoder, create_folder

DUMP_METHOD_PATTERN = "_dump_{}_"
RESTORE_METHOD_PATTERN = "_restore_{}_"


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
        for prefix in ("PICKLE_BLACKLIST", "CONFIG_ITEMS"):
            # If the class has a prefix attribute, it will be used as it is
            # we convert it to a set to prevent duplicated values
            if prefix in attributes:
                pickle_blacklist = {key for key in attributes[prefix]}

            # Otherwise the prefix attribute will be created from the parent classes
            # prefix attributes and the {prefix}_ADD and {prefix}_REMOVE attributes
            else:
                pickle_blacklist = set()

                # First we get the union of all pickle_blacklist of the parents
                for parent in parents:
                    if issubclass(parent, Archivable):
                        pickle_blacklist = pickle_blacklist.union(
                            getattr(parent, prefix, set())
                        )

                # Then we add attributes from {prefix}_ADD
                pickle_blacklist = pickle_blacklist.union(
                    attributes.get(f"{prefix}_ADD", set())
                )
                # and we remove attributes from {prefix}_REMOVE
                pickle_blacklist = pickle_blacklist.difference(
                    attributes.get(f"{prefix}_REMOVE", set())
                )

            # Finnaly, {prefix} is converted to a tuple for immutablity
            attributes[prefix] = tuple(sorted(pickle_blacklist))

        return super().__new__(cls, name, parents, attributes)


class Archivable(metaclass=MetaArchivable):
    PICKLE_NAME: str = "archive.pkl"
    PICKLE_BLACKLIST: Iterable[str] = ()
    PICKLE_BLACKLIST_ADD: Iterable[str] = ()
    PICKLE_BLACKLIST_REMOVE: Iterable[str] = ()

    CONFIG_NAME: str = "config.json"
    CONFIG_ITEMS: Iterable[str] = ()
    CONFIG_ITEMS_ADD: Iterable[str] = ()
    CONFIG_ITEMS_REMOVE: Iterable[str] = ()

    @property
    def configurations(self) -> dict:
        """A configuration dict used to show important attributes

        Returns:
            dict: configuration dict
        """
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
        overwrite: bool = True,
    ):
        """Save the object instance in a dedicated directory

        Args:
            path (Union[str, Path]): Path to the directory
            pickle_dump_kwargs (dict, optional): kwargs to be passed to
                pickle.dump method. Defaults to None.
            json_dump_kwargs (dict, optional): kwargs to be passed to json.dump method.
                Defaults to None.
            overwrite (bool, optional): If True, overwrite the folder if it exists.
        """
        # Before save hook
        self.before_save()

        path = create_folder(path)

        if pickle_dump_kwargs is None:
            pickle_dump_kwargs = {}

        if json_dump_kwargs is None:
            json_dump_kwargs = {}

        self.save_instance(path, overwrite=overwrite, **json_dump_kwargs)
        self.save_config(path, overwrite=overwrite, **json_dump_kwargs)
        self.save_pickle_blacklisted(path, overwrite=overwrite)

        # After save hook
        self.after_save()

    def before_save(self):
        """Hook executed at the beggining of the save method"""

    def after_save(self):
        """Hook executed at the end of the save method"""

    def save_instance(self, path: Union[str, Path], overwrite: bool = True, **kwargs):
        """Save the current instance

        Args:
            path (Union[str, Path]): path to a folder where to save the current instance
            overwrite (bool, optional): If True, overwrite the folder if it exists.
        """
        if not self.PICKLE_NAME:
            logger.info(
                f"{self.__class__.__name__}.PICKLE_NAME is empty so the instance "
                f"will not be saved"
            )
            return

        path = create_folder(path)
        filepath = path / self.PICKLE_NAME

        if overwrite or not filepath.exists():
            with open(filepath, "wb") as f:
                pickle.dump(self, f, **kwargs)

    def save_config(
        self,
        path: Union[str, Path],
        overwrite: bool = True,
        indent: int = 2,
        cls: json.JSONEncoder = NumpyJSONEncoder,
        **kwargs,
    ):
        """Save the instance configuration attributes

        Args:
            path (Union[str, Path]): path to a folder where to save the current instance
                config file
            overwrite (bool, optional): If True, overwrite the folder if it exists.
            indent (int, optional): JSON indentation. Defaults to 2.
            cls (JSONEncoder, optional): JSON encoder object.
                Defaults to NumpyJSONEncoder.
        """
        if not self.CONFIG_NAME:
            logger.info(
                f"{self.__class__.__name__}.CONFIG_NAME is empty so the configuration "
                f"dict will not be saved"
            )
            return

        path = create_folder(path)
        filepath = path / self.CONFIG_NAME

        if overwrite or not filepath.exists():
            with open(filepath, "w") as f:
                json.dump(self.configurations, f, indent=indent, cls=cls, **kwargs)

    def save_pickle_blacklisted(
        self, path: Union[str, Path], overwrite: bool = True
    ) -> Dict[str, Exception]:
        """Try to save excluded attributes

        Args:
            path (Union[str, Path]): path to a folder where to save blacklisted
                attributes
            overwrite (bool, optional): If True, overwrite the folder if it exists
        Returns:
            Dict[str, Exception]: A dictionary of attributes that could not be saved
                and corresponding exceptions raised
        """
        path = create_folder(path)
        failures = {}

        for attribute in self.PICKLE_BLACKLIST:
            try:
                getattr(self, DUMP_METHOD_PATTERN.format(attribute))(
                    path, overwrite=overwrite
                )
            except DumpAttributeError as e:
                logger.warning(
                    f"{self.__class__.__name__}"
                    f".{DUMP_METHOD_PATTERN.format(attribute)} failed : "
                    f"self.{attribute} could not be dumped"
                )
                logger.exception(e)
                failures[attribute] = e
            except AttributeError as e:
                logger.debug(
                    f"self.{attribute} count not be dumped since there is no "
                    f"method {self.__class__.__name__}"
                    f".{DUMP_METHOD_PATTERN.format(attribute)}"
                )
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

    @classmethod
    def before_load(cls):
        """Hook executed at the beggining of the load method"""

    @classmethod
    def after_load(cls):
        """Hook executed at the end of the load method"""

    def load_pickle_blacklisted(self, path: Union[str, Path]) -> Dict[str, Exception]:
        """Try to unpickle excluded attributes

        Args:
            path (Union[str, Path]): Path to the pickle file

        Returns:
            Dict[str, Exception]: A dictionary of attributes that could not be loaded
                and corresponding exceptions raised
        """
        failures = {}
        for attribute in self.PICKLE_BLACKLIST:
            try:
                getattr(self, RESTORE_METHOD_PATTERN.format(attribute))(path)
            except RestoreAttributeError as e:
                logger.warning(
                    f"{self.__class__.__name__}"
                    f".{RESTORE_METHOD_PATTERN.format(attribute)} failed : "
                    f"self.{attribute} could not be restored"
                )
                logger.exception(e)
                failures[attribute] = e
            except AttributeError as e:
                logger.debug(
                    f"self.{attribute} count not be unpickled since there is no "
                    f"method {self.__class__.__name__}"
                    f".{RESTORE_METHOD_PATTERN.format(attribute)}"
                )
                failures[attribute] = e

        return failures
