# Development Information

You want to contribute to the UniverSQL API itself? This file contains information about the detailled structure that might be helpful to do so.

## Translators directory
The directory `translators` contains the original system repositories as git submodules. It should not be necessary to modify anything. More important, all changes will be local. So be aware not to include
changes in a commit.

## Django Application File Structure
The project consists of a single app. Inside this app, the structure follows the Django standards, i.e. the following files exist
and serve their normal purposes (see: https://www.djangoproject.com/):
```
migrations/
admin.py
apps.py
models.py
test.py
urls.py
views.py
```

The directories `nlidbTranslator/api/adapters` and `nlidbTranslator/api/schemas` hold the custom extensions as described in the [documentation about extensions](Extension.md)

Following is an overview of project specific files and their relations. It is meant to help finding the right point to make changes in the code.

### Responsibilities

File | Responsibility
------------|----------
| `nlidbTranslator/api/__init__.py` | adds paths to the python path to allow  absolute paths that don't start in the root directory of the project
| `nlidbTranslator/api/analysis.py` | collect information about available adapters and schemas
| `nlidbTranslator/api/paths.py` | hold useful path constants
| `nlidbTranslator/api/process_request.py` | perform low-level processing of requests as instructed by the views
| `nlidbTranslator/api/serializers.py` | define serializers for input and output of the API
| `nlidbTranslator/api/setup_util.py` | 1) perform pre-loading of the glove 
| | 2) download necessary nltk packages
| | 3) write combined schema file (a concatenation of all available schemas)
| | 4) call the setup function of each system and store the mapping to the corresponding interface functions


### Dependencies
`__init__.py` is the first file in the app directory that is executed. This file adds paths to the python path.
The order of execution is important here because the paths need to be added before `setup_util` is executed. The reason for this is, that
`setup_util` calls the adapter code, which propagates the call to the original system in some form. Both rely on
the ability to import with absolute imports, but from directories other than the project root.

The execution of `__init__` leads to the import of `analysis` and `paths`:
```
paths.py -> analysis.py -> __init__.py
```

When Django tries to access `models`, it causes `setup_util` to load, which can use the already loaded `analysis`:
```
analysis.py -> setup_util.py -> models.py
```

Finally `views` builds on functionality in `process_request`, which needs both `models` and `serializers` to be loaded:
```
models.py -> serializers.py -> process_request.py -> views.py 
```


### Volatile Files
Changes are likely to be necessary in the following files:

File | Reason to change
------------|----------
| `nlidbTranslator/api/models.py` | 1) add a new model, e.g. as a data structure for a new challenge
| | 2) change an existing model to include more information
| `nlidbTranslator/api/paths.py` | add a new global path
| `nlidbTranslator/api/process_request.py` | refine low-level processing of requests that originate from `views`
| `nlidbTranslator/api/serializer.py` | 1) add a new serializer for a new model
| | 2) change the fields list of an existing serializer
| `nlidbTranslator/api/tests.py` | add test cases
| `nlidbTranslator/api/urls.py` | 1) add a new basic endpoint, e.g. to deal with a new challenge
| | 2) change the structure of the current url paths
| `nlidbTranslator/api/views.py` | 1) define processing of requests, e.g. in the context of a new challenge
| | 2) change the high-level processing of requests


## Notes on Models
   - By default Django adds a primary key in the form of a field `id` to all models. For the model `Translation` this field
   is unambiguously used throughout the application. The model `Interaction` has also a similar field named `interaction_id`.
   However the integer value of this field denotes the "id" of the interaction to which the single item belongs. This `interaction_id`
   is used to group all instances of the same interaction, when displayed for the logs. Whereas `id` is referenced only internally when it is necessary to access an individual item, e.g. to delete it.
   Please be aware of this difference.


## Import Paths
The root path of the Django project is `universql/nlidbTranslator`. So to access any module from the application directory, the import path must start
with `api` (which is the name of the app). For example:
```
from api.paths import SCHEMAS_DIR
```
