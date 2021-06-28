import os
from pathlib import Path

from api.paths import TRANSLATORS_DIR

CURRENT_DIR = os.path.dirname(__file__)


#Paths
IRNET_BASE_DIR = Path(TRANSLATORS_DIR) / "IRNet"
PATH_TO_CONCEPTNET = str(Path(IRNET_BASE_DIR) / "./conceptNet/")
PATH_TO_PRETRAINED_MODEL = Path(IRNET_BASE_DIR) / "saved_model" / "IRNet_pretrained.model"




