## Specifying attributes that should not be pickled

The main feature of `vipickle` is the ability to pickle any object thanks to a `PICKLE_BLACKLIST` class attribute :

```python hl_lines="4"
from vipickle import VIPicklable

class MyClass(VIPicklable):
    PICKLE_BLACKLIST = ["unpicklable_attribute"]

    def __init__(self):
        self.unpicklable_attribute = "do_not_pickle"
```

All attributes specified in `PICKLE_BLACKLIST` will no be included in the pickled file :

```pycon
>>> import pickle
>>>
>>> obj = MyClass()
>>> assert obj.unpicklable_attribute == "do_not_pickle"
>>>
>>> with open("obj.pkl", "wb") as f:
...    pickle.dump(obj, f)
...
>>> with open("obj.pkl", "rb") as f:
...    obj = pickle.load(f)
...
>>> obj.unpicklable_attribute
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'MyClass' object has no attribute 'unpicklable_attribute'
```

## Inheritance

As any class attribute `PICKLE_BLACKLIST` will be inherited by all subclasses.

It would be annoying to redefine `PICKLE_BLACKLIST` in each subclasses to add or remove some attributes from the list so
`vipickle` introduce two class attributes for doing so

### `PICKLE_BLACKLIST_ADD`

```python hl_lines="2"
class MySubClass(MyClass):
    PICKLE_BLACKLIST_ADD = ["another_unpicklable_attribute"]

    def __init__(self):
        super(MySubClass, self).__init__()
        self.another_unpicklable_attribute = "do_not_pickle"
```

### `PICKLE_BLACKLIST_REMOVE`

```python hl_lines="2"
class MySubSubClass(MySubClass):
    PICKLE_BLACKLIST_REMOVE = ["unpicklable_attribute"]

    def __init__(self):
        super(MySubSubClass, self).__init__()
```

!!! warning
    If `PICKLE_BLACKLIST` is present, neither `PICKLE_BLACKLIST_ADD` nor `PICKLE_BLACKLIST_REMOVE` will be taken into
    account
