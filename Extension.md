# Extension: Add support for other approaches

## Adapter

Adapters serve as the glue between independent systems, e.g. IRNet or EditSQL, and the Django application, which runs the API.
For every system you need to write one adapter to make this system available as an option in the API.

### Preparation

For a system named `system_name`:

1. Insert the root directory `system_name` of your system into the directory `/translators`

2. Create a directory with the same name in the directory `nlidbTranslator/api/adapters`.

Now you should have the two directories:
`/translators/system_name` and `/nlidbTranslator/api/adapters/system_name`.

### Implementation

1. Inside your directory `/nlidbTranslator/api/adapters/system_name` provide a file **`interface.py`** with two mandatory functions:
    - **`setup()`** which gets called once and may be used for setup
    - **`translate(nl_question, db_id)`** which returns the SQL as a string

2. _Optional_: add a translate function for interactions, which will also receive the previous utterances and
predictions belonging to the same interaction (each as a list)
    - `translate_interaction(nl_question, db_id, prev_nl_questions, prev_predictions)`
    
    Again the returned SQL must be a single string.


You may populate your adapters directory with any number of files, as long as this contract above is fulfilled.

#### Import Paths
This section describes how to import from various places in the project to any file inside your adapters directory `/nlidbTranslator/api/adapters/system_name`.

_Note: The following information is for imports into your adapters directory. Regarding importing in your original system you don't need to change anything. By the time you write the system, just pretend the system's root directory is also the import path root.
The application will do everything necessary to allow these imports to work in the environment of the application too._

The root path of the Django project is `universql/nlidbTranslator`. So to access any module **from the application directory**, the import path must start
with `api` (which is the name of the app). For example:
```
from api.paths import SCHEMAS_DIR
```


Additionally two shortcuts exist for convenience:

To import modules **from the original system**, i.e. form `/translators/system_name`, prefix the import path with `system_name` .
For example:
```
from IRNet.sem2SQL import transform
```

If you need to access code **from somewhere else in the adapter**, import `adapters.adapter_name.module_name`. For example:
```
from adapters.editsql import constants
```


#### Shared Objects
Containing Module | Object | What it is
---|-----|----
| `nlidbTranslator/api/analysis.py` | `schemas` |  dict from schema name to the loaded data defined by any json file in `/nlidbTranslator/api/schemas`
| `nlidbTranslator/api/analysis.py` | `schema_column_names` |   dict from schema name to a dict from table name to column names
| `nlidbTranslator/api/setup_util.py` | `glove_embeddings` |  pre-loaded glove for usage in your system
| `nlidbTranslator/api/setup_util.py` | `@no_stdout` |   decorator to silent any output of a function (e.g. logs from the original system)


## Schema
All schemas files must be lists of dictionaries in a specific format. You can create your own schema based on the
existing one in `nlidbTranslator/api/schemas`.

For example choose `nlidbTranslator/api/schemas/spider_tables.json`. Then copy, delete and modify what is necessary.
Just make sure, that the original template is maintained.

To add your custom schema, place the json file inside `nlidbTranslator/api/schemas`. It will be automatically recognized
and made available as an option for API requests.
