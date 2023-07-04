## Loading an VIPicklable object

[`VIPicklable`](/reference/vipickle/mixin/#vipickle.mixin.VIPicklable) objects have a
[`load method`](/reference/vipickle/mixin/#vipickle.mixin.VIPicklable.load) for loading an object instance :

```pycon
>>> class MyClass(VIPicklable):
...    PICKLE_BLACKLIST = ["unpicklable_attribute"]
...
...    def __init__(self):
...        self.unpicklable_attribute = "do_not_pickle"
...
>>> obj = MyClass()
>>> obj.save("folder")
>>> obj = MyClass.load("folder")
```

??? abstract "VIPicklable.load"

    ::: vipickle.mixin.VIPicklable.load
