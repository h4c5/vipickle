## Saving a VIPicklable object

[`VIPicklable`](/vipickle/reference/vipickle/mixin/#vipickle.mixin.VIPicklable) objects have a
[`save method`](/vipickle/reference/vipickle/mixin/#vipickle.mixin.VIPicklable.save) for saving an object instance :

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

### Save hooks

Under the hood, the save method does the following :

```mermaid
stateDiagram-v2
    [*] --> self.before_save()
    self.before_save() --> self.save_instance()
    self.save_instance() --> self.save_config()
    self.save_config() --> self.save_pickle_blacklisted()
    self.save_pickle_blacklisted() --> self.after_save()
    self.after_save() --> [*]
```

One can redefine any of these methods to personnalise the saving process :

-   [before_save](/vipickle/reference/vipickle/mixin#vipickle.mixin.VIPicklable.before_save)
-   [save_instance](/vipickle/reference/vipickle/mixin#vipickle.mixin.VIPicklable.save_instance)
-   [save_config](/vipickle/reference/vipickle/mixin#vipickle.mixin.VIPicklable.save_config)
-   [save_pickle_blacklisted](/vipickle/reference/vipickle/mixin#vipickle.mixin.VIPicklable.save_pickle_blacklisted)
-   [after_save](/vipickle/reference/vipickle/mixin#vipickle.mixin.VIPicklable.after_save)
