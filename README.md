<div align="center">
    <img src="https://img.shields.io/pypi/v/blackpickle" alt="blackpickle package version" />
    <img src="https://img.shields.io/pypi/pyversions/blackpickle" alt="Python supported versions" />
    <a href="https://github.com/PyCQA/bandit">
        <img src="https://img.shields.io/badge/security-bandit-yellow.svg" alt="Security thanks to bandit package" />
    </a>
    <img src="https://img.shields.io/badge/formatting-black-black" alt="Black formatting" />
</div>

<div align="center">
    <h1>BlackPickle</h1>
    <p ><b>Tiny python package for saving instances with unpickable attributes</b></p>
</div>

## Quickstart

Install `blackpickle` with pip :
```bash
pip install blackpickle
```

Then inherit from `Archivable` and define which attribute are not picklable and how they should be dumped and restored.

```python
import torch
from torchvision import models
from pathlib import Path

from blackpickle import Archivable

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

```

## Additionnal dependencies

#### Dev dependencies
```bash
pip install blackpickle[dev]
```

#### Unit tests dependencies
```bash
pip install blackpickle[test]
```

#### Documentation dependencies
```bash
pip install blackpickle[doc]
```
