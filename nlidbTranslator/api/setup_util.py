import json
import os
import sys
import numpy as np
import importlib
from pathlib import Path
from api.analysis import translators, schemas
from api.paths import GLOVE_FILE, DB_SCHEMAS_FILE, PROJECT_ROOT

import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')



# load the glove file
THRESHOLD = 500000
# source: https://github.com/microsoft/IRNet
def load_word_emb(file_name, use_small=False):
    print('Loading word embedding from %s' % file_name)
    ret = {}
    with open(file_name) as inf:
        for idx, line in enumerate(inf):
            if use_small and idx >= THRESHOLD:
                break
            info = line.strip().split(' ')
            if info[0].lower() not in ret:
                ret[info[0]] = np.array(list(map(lambda x: float(x), info[1:])))
    return ret

glove_embeddings = load_word_emb(GLOVE_FILE, use_small=True)


# concatenate all schema files to one file
tables = []

for schema in schemas.values():
    tables.append(schema)

# write the total to a file for use in read_database_schema()
with open(DB_SCHEMAS_FILE, 'w') as f:
    json.dump(tables, f, indent=4)


# decorator used to send translator stdout to void
def no_stdout(func):
    def wrapper(*args, **kwargs):
        stdout = sys.stdout
        f = open(os.devnull, 'w')
        sys.stdout = f

        value = func(*args, **kwargs)

        sys.stdout = stdout

        return value

    return wrapper


# for each adapter:
# dynamically access the functions defined in interface.py
# to call setup() once and
#    store the reference to translate() in a dict
adapters_dict = {}
int_translators = []

for translator in translators:
    # access the specific module
    path = "api.adapters.{}.interface".format(translator)
    module = importlib.import_module(path)

    # single call to setup()
    module.setup()

    # store reference to translate() for later use by view.py
    adapters_dict[translator] = dict()
    adapters_dict[translator]["translate"] = module.translate
    if hasattr(module, "translate_interaction"):
        adapters_dict[translator]["interaction"] = module.translate_interaction
        int_translators.append(translator)

