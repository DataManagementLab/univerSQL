import json
import os
import warnings

from api.paths import ADAPTERS_DIR, SCHEMAS_DIR


# helper function
def list_of_files(directory, extension=""):
    names = []

    for filename in os.listdir(directory):
        if not extension:
            names.append(filename)
        elif filename.endswith(extension):
            names.append(filename.split(extension)[0])

    return names

# list of available translators based on files
translators = list_of_files(directory=ADAPTERS_DIR)

schema_files = list_of_files(directory=SCHEMAS_DIR, extension=".json")
schemas = {}
for schema_f in schema_files:
    # access schema definitions list
    with open(os.path.join(SCHEMAS_DIR, schema_f + ".json")) as infile:
        schema_list = json.load(infile)

    # restructure the list into a dict according to the database id
    schema_dict = {}
    for entry in schema_list:
        value_for_key = entry["db_id"]
        schema_dict[value_for_key] = entry

    # check for duplicates
    for db_id in schema_dict:
        if db_id in schemas:
            warnings.warn("Overwriting schema definition for duplicate! name: " + db_id)

    # add the schema definitions from this iteration to the overall collection
    schemas.update(schema_dict)


# store the mapping of table name to column names for each schema
schema_column_names = dict()
for schema_name in schemas:
    table_names = schemas[schema_name]["table_names_original"]
    column_tuples = schemas[schema_name]["column_names_original"]
    column_names = dict()
    for idx, table_name in enumerate(table_names):
        table_columns = [c[1] for c in column_tuples if c[0] == idx]
        column_names[table_name] = table_columns
    schema_column_names[schema_name] = column_names