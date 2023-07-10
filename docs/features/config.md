## Configuration file

It can be very handy to have save some attributes in a JSON file (which is human readable) so `vipickle` helps you with
that :

```python hl_lines="4"
from vipickle import VIPicklable

class MyClass(VIPicklable):
    CONFIG_ITEMS = ["param"]

    def __init__(self):
        self.param = 0.1
```

When a `MyClass` is saved thanks to the `save` method, a `config.json` is created with all specified attributes

```pycon
>>> obj = MyClass()
>>> obj.save("dir")
```

```json title="dir/config.json"
{
    "param": 0.1
}
```

`VIPicklable` have a `configurations` dict property that contains all attributes listed in `CONFIG_ITEMS`

## Inheritance

Just like the attribute `PICKLE_BLACKLIST`, `CONFIG_ITEMS` will be inherited by all subclasses.

It would be annoying to redefine `CONFIG_ITEMS` in each subclasses to add or remove some attributes from the list so
`vipickle` introduce two class attributes for doing so

### `CONFIG_ITEMS_ADD`

```python hl_lines="2"
class MySubClass(MyClass):
    CONFIG_ITEMS_ADD = ["another_config_attribute"]

    def __init__(self):
        super(MySubClass, self).__init__()
        self.another_config_attribute = "param"
```

### `CONFIG_ITEMS_REMOVE`

```python hl_lines="2"
class MySubSubClass(MySubClass):
    CONFIG_ITEMS_REMOVE = ["another_config_attribute"]
```

!!! warning
    If `CONFIG_ITEMS` is present, neither `CONFIG_ITEMS_ADD` nor `CONFIG_ITEMS_REMOVE` will be taken into account