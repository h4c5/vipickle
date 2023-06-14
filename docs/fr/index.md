# VIPickle

VIPicle permet de sauvegarder des instances de classes qui ont des attributs non "picklable".

## Démarrage

Installation de `vipickle` avec pip :

```bash
pip install vipickle
```

Il vous suffit ensuite d'hériter de la classe VIPicklable `VIPicklable` et de spécifier les attributs qui ne doivent pas
être "picklés".

Vous pouvez également spécifier des fonctions de sauvegarder et de chargement alternatives pour ces attributs afin de
restaurer l'instance.

```python
import torch
from torchvision import models
from pathlib import Path

from vipickle import VIPicklable

class MyClass(VIPicklable):
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

## Dépendances optionnelles

#### Dépendances de développement

```bash
pip install vipickle[dev]
```

#### Dépendances de test

```bash
pip install vipickle[test]
```

#### Dépendances de documentation

```bash
pip install vipickle[doc]
```
