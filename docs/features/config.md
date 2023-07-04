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
