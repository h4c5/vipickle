# VIPickle

vipickle is tiny python package for saving instances with unpickable attributes and restore them later.

## Installation

Install [`vipickle`](https://pypi.org/project/vipickle/) with pip :

```bash
pip install vipickle
```

## Quickstart

Inherit from `VIPicklable` to add saving and reloading capabilites to yours objects even if they have unpickable
attributes.

```python
from vipickle import VIPicklable

class MyClass(VIPicklable):
    PICKLE_BLACKLIST = ["unpicklable_attribute"]

    def __init__(self):
        self.unpicklable_attribute = "do_not_pickle"

    def _dump_unpicklable_attribute_(self, save_dir: Path, overwrite:bool = True):
        print("unpicklable_attribute won't be pickled but we could have saved it another way")

    def _restore_unpicklable_attribute_(self, save_dir: Path):
        self.unpicklable_attribute = "attribute_restored"


# Create an instance
obj = Myclass()
assert obj.unpicklable_attribute == "do_not_pickle"

# Save it : _dump_unpicklable_attribute_ will print a message
obj.save("a/folder")
del obj

# Reload the object instance : _restore_unpicklable_attribute_ will set unpicklable_attribute
obj = MyClass.load("a/folder")
assert obj.unpicklable_attribute == "attribute_restored"
```

## Features

-   Blacklist of attributes that should not be pickled
-   Dumping methods for blacklisted attributes
-   Loading methods for blacklisted attributes
-   List of attributes to be saved in a JSON file
-   Blacklist inheritance

See [Features](features/blacklist/) section for more details

## Development

Clone the repository and create a virtual environement

```bash
git clone https://github.com/h4c5/vipickle
cd vipickle
python -m venv .venv
```

Activate the virtual environment and install dev dependencies :

```bash
source .venv/bin/activate
pip install vipickle[dev]
```

Make modifications.

To build the documentation, first install the documentation dependencies :

```bash
pip install vipickle[doc]
```

Then :

```bash
mkdocs serve # for local serving
mkdocs build # to build documentation
```
