## Saving a VIPicklable object

[`VIPicklable`](/reference/vipickle/mixin/#vipickle.mixin.VIPicklable) objects have a
[`save method`](/reference/vipickle/mixin/#vipickle.mixin.VIPicklable.save) for saving an object instance :

```pycon
>>> class MyClass(VIPicklable):
...    PICKLE_BLACKLIST = ["unpicklable_attribute"]
...
...    def __init__(self):
...        self.unpicklable_attribute = "do_not_pickle"
...
>>> obj = MyClass()
>>> obj.save("folder")
```

??? abstract "VIPicklable.save"

    ::: vipickle.mixin.VIPicklable.save
