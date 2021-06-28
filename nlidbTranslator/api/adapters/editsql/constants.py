import os
from pathlib import Path

from api.paths import TRANSLATORS_DIR
from editsql.data_util import atis_data

CURRENT_DIR = Path(os.path.dirname(__file__))

EDITSQL_BASE_DIR = Path(TRANSLATORS_DIR) / "editsql"

EVAL_REFERENCE_FILE = Path(CURRENT_DIR / "evaluation/reference.json")
BATCH_INPUT_FILE = Path(CURRENT_DIR / "batch_processing/input.json")
BATCH_OUTPUT_DIR = Path(CURRENT_DIR / "batch_processing/output")


# overwrite the path constants in atis_data
atis_data.ENTITIES_FILENAME = str(EDITSQL_BASE_DIR / "data/entities.txt")
atis_data.ANONYMIZATION_FILENAME = str(EDITSQL_BASE_DIR / "data/anonymization.txt")
