import re
from pathlib import Path

from nlidbTranslator.settings import BASE_DIR, PROJECT_ROOT



TRANSLATORS_DIR = Path(PROJECT_ROOT / "translators")
GLOVE_FILE = Path(TRANSLATORS_DIR, "glove.42B.300d.txt")

ADAPTERS_DIR = Path(BASE_DIR / "api/adapters")
SCHEMAS_DIR = Path(BASE_DIR / "api/schemas")
DB_SCHEMAS_FILE = Path(SCHEMAS_DIR / "processed/tables.json")
