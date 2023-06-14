# VIPickle

vipickle is tiny python package for saving instances with unpickable attributes and restore them later.

## Quickstart

Install `vipickle` with pip :

```bash
pip install vipickle
```

Then inherit from `Archivable` and define which attribute are not picklable and how they should be dumped and restored.

```python
import torch
from torchvision import models
from pathlib import Path

from vipickle import Archivable

class MyClass(Archivable):
    PICKLE_BLACKLIST = ["vision_model"]

    def __init__(self):
        self.vision_model = models.vgg16(weights='IMAGENET1K_V1')

    def _dump_vision_model_(self, save_dir: Path, overwrite:bool = True):
        model_weights_path = save_dir / "model_weights.pth"
        if overwrite or not model_weights_path.exists():
            torch.save(model.state_dict(), model_weights_path)

    def _restore_vision_model_(self, save_dir: Path):
        self.vision_model = models.vgg16()
        self.vision_model.load_state_dict(torch.load(save_dir / "model_weights.pth"))


# Create an instance
obj = Myclass()

# train could modify the model weights
obj.train()

# we save the instance to a folder, _dump_vision_model_ will dump the weights in the folder
obj.save("a/folder")
del obj

# we can then reload the object, _restore_vision_model_ will recreate the attribute vision_model and load the weights
obj = MyClass.load("a/folder")
obj.vision_model.eval()
```

## Additionnal dependencies

#### Dev dependencies

```bash
pip install vipickle[dev]
```

#### Unit tests dependencies

```bash
pip install vipickle[test]
```

#### Documentation dependencies

```bash
pip install vipickle[doc]
```
