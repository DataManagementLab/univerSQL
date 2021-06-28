import sys

from api.analysis import translators
from api.paths import PROJECT_ROOT


# allow for imports of translator code as "translator.module"
sys.path.append(str(PROJECT_ROOT / "translators"))

# allow for imports of adapter code as "adapter.translator.module"
sys.path.append(str(PROJECT_ROOT / "nlidbTranslator/api"))


# preserve functioning of all original imports in the translators (relative to their root)
for translator in translators:
    path_to_translator = str(PROJECT_ROOT / "translators" / translator)

    if path_to_translator not in sys.path:
        sys.path.append(path_to_translator)
