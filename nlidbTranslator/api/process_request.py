import sqlparse

from analysis import schemas
from api.setup_util import adapters_dict
from api.models import Translation, Interaction
from api.serializers import TranslationSerializer, InteractionSerializer, UtteranceSerializer
from rest_framework.exceptions import ValidationError


def format_sql(sql_statement):
    return sqlparse.format(sql_statement, reindent=False, keyword_case='upper', strip_whitespace=True)


def store_translation(nl_question, db_schema, translator):
    """
        Stores a Translation in the database

        Args:
            nl_question: question as a string
            db_schema: database name
            translator: translator name

        Returns:
            serializer data for this same Translation
    """
    # get the right translation function
    translate = adapters_dict[translator]['translate']

    # use the function to translate
    sql_statement = translate(nl_question, db_schema)
    formatted = format_sql(sql_statement)

    translation = Translation(
        nl_question=nl_question,
        sql_statement=formatted,
        db_schema=db_schema,
        translator=translator,
    )
    translation.save()

    serializer = TranslationSerializer(translation)
    return serializer.data


def store_interaction(int_id, prev_utterances, nl_question, db_schema, translator, url):
    """
        Stores an Interaction in the database

        Args:
            int_id: interaction id
            prev_utterances: list of previous utterances (using UtteranceSerializer)
            nl_question: question as a string
            db_schema: database name
            translator: translator name
            url: full url to the interaction

        Returns:
            serializer data for this same Interaction
    """
    # collect information about the context of the interaction
    prev_questions = []
    prev_predictions = []
    if prev_utterances:
        translator = prev_utterances[0].translator      # ignore function parameter and overwrite
        db_schema = prev_utterances[0].db_schema        # ignore function parameter and overwrite
        prev_questions = [i.nl_question for i in prev_utterances]
        prev_predictions = [i.sql_statement for i in prev_utterances]

    # get the right translation function
    translate_interaction = adapters_dict[translator]['interaction']

    # use the function to translate
    sql_statement = translate_interaction(nl_question, db_schema, prev_questions, prev_predictions)
    formatted = format_sql(sql_statement)

    interaction = Interaction(
        url=url,
        interaction_id=int_id,
        nl_question=nl_question,
        sql_statement=formatted,
        db_schema=db_schema,
        translator=translator,
    )
    interaction.save()

    serializer = InteractionSerializer(interaction)
    return serializer.data


def group_interaction_items(interactions_queryset):
    """
        Create an overview of the interaction instances grouped by interaction_id

        Args:
            interactions_queryset: queryset of interactions

        Returns:
            list of interaction details sorted by interaction_id asc
    """
    # order queryset to list the utterances chronologically
    interactions_queryset = interactions_queryset.order_by("created")

    interactions_overview = dict()
    for interaction in interactions_queryset:
        utterance = UtteranceSerializer(interaction).data
        if interaction.interaction_id not in interactions_overview:
            # create a new entry with the data of this interaction
            interactions_overview[interaction.interaction_id] = {
                "url": interaction.url,
                "interaction_id": interaction.interaction_id,
                "translator": interaction.translator,
                "db_schema": interaction.db_schema,
                "interaction": [utterance]
            }
        else:
            # add the data for nl_question and sql_statement to the existing list of utterances
            interactions_overview[interaction.interaction_id]["interaction"].append(utterance)

    # sort by interaction_id desc
    sorted_keys = sorted(interactions_overview, reverse=True)
    return [interactions_overview[k] for k in sorted_keys]


def get_single_interaction_details(queryset, int_id):
    """
        Get compact details for one interaction instance

        Args:
            queryset: queryset of all interactions
            int_id: id of the interaction that should be considered

        Returns:
            compact details for one interaction
    """
    # limit the interaction overview to one interaction_id
    filtered = queryset.filter(interaction_id=int_id)
    int_details = group_interaction_items(filtered)

    if not int_details:
        return None
    return int_details[0]


def check_params_exist_and_not_empty(request_data, required_params):
    """
        Will raise a Bad Request Error (400) if not all strings in required_params are present as keys in request_data or any value for a key is empty
    """
    missing = [p for p in required_params if p not in request_data]
    if missing:
        raise ValidationError(detail="Missing parameters: {}".format(missing))

    empty = [p for p in required_params if request_data[p] == ""]
    if empty:
        raise ValidationError(detail="No value for parameters {}".format(empty))


def check_choices_valid(database_id, translator, operation_name):
    """
        Will raise a Bad Request Error (400) if database_id or translator are no valid choices or the translator does not support the operation

    """
    if database_id not in schemas:
        raise ValidationError(detail="Database name unknown: {}".format(database_id))

    if translator not in adapters_dict:
        raise ValidationError(detail="Translator name unknown: {}".format(translator))

    if operation_name not in adapters_dict[translator]:
        raise ValidationError(detail="Unsupported operation for {}: {}".format(translator, operation_name))