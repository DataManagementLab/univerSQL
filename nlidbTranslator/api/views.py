from django.urls import reverse
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser

from api.analysis import schemas, schema_column_names, translators
from api.setup_util import int_translators
from api.models import Translation, Interaction
from api.serializers import TranslationSerializer, InteractionSerializer, UtteranceSerializer
from api.process_request import store_translation, store_interaction, group_interaction_items, \
    get_single_interaction_details, check_params_exist_and_not_empty, check_choices_valid


class Translate(generics.CreateAPIView):
    """
        Translates a natural language question to sql

        For this you need to provide:
        - the id of the database schema (see /schemas)
        - the id of the translator (see /translators)
    """
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer

    def post(self, request):
        check_params_exist_and_not_empty(request_data=request.data,
            required_params=['nl_question', 'db_schema', 'translator'])
        check_choices_valid(database_id=request.data['db_schema'],
            translator=request.data['translator'], operation_name="translate")

        response_data = store_translation(
            nl_question=request.data['nl_question'],
            db_schema=request.data['db_schema'],
            translator=request.data['translator']
        )
        return Response(response_data)


class StartInteraction(GenericAPIView):
    """
        Start an interaction

        For this you need to provide:
        - the id of the database schema (see /schemas)
        - the id of the interaction translator (see /translators)
    """
    queryset = Interaction.objects.all().order_by("-interaction_id")
    serializer_class = InteractionSerializer

    def post(self, request):
        check_params_exist_and_not_empty(request_data=request.data,
            required_params=['nl_question', 'db_schema', 'translator'])
        check_choices_valid(database_id=request.data['db_schema'],
            translator=request.data['translator'], operation_name="interaction")

        # set the next interaction_id to be the currently highest value incremented by 1
        if self.queryset.all():
            next_int_id = self.queryset.all()[0].interaction_id + 1
        else:
            next_int_id = 0

        response_data = store_interaction(
            url=request.build_absolute_uri(reverse("interaction", args=[str(next_int_id)])),
            int_id=next_int_id,
            prev_utterances=[],
            nl_question=request.data['nl_question'],
            db_schema=request.data['db_schema'],
            translator=request.data['translator']
        )
        return Response(response_data)


class TranslateInteraction(GenericAPIView):
    """
        Add utterances to an interaction and view all predictions
    """
    queryset = Interaction.objects.all()
    serializer_class = UtteranceSerializer

    def get(self, request, int_id):
        prev_utterances = self.queryset.filter(interaction_id=int_id)
        if not prev_utterances.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(get_single_interaction_details(self.queryset, int_id))

    def post(self, request, int_id):
        check_params_exist_and_not_empty(request_data=request.data,
            required_params=['nl_question'])

        # get the previous utterances that belong to the same interaction
        prev_utterances = self.queryset.filter(interaction_id=int_id).order_by("created")

        if not prev_utterances.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data="You first have to start an interaction before you can continue it.")

        _ = store_interaction(
            url=request.build_absolute_uri(reverse("interaction", args=[str(int_id)])),
            int_id=int_id,
            prev_utterances=prev_utterances,
            nl_question=request.data['nl_question'],
            db_schema=None,
            translator=None
        )
        return self.get(request, int_id)


class TranslateLogList(generics.ListAPIView):
    """
        List either all stored translations or only the `n` most recent
    """
    permission_classes = [IsAdminUser]

    serializer_class = TranslationSerializer

    def get_queryset(self):
        queryset = Translation.objects.all().order_by("-created")

        if "n" in self.kwargs:
            return queryset[:self.kwargs["n"]]  # consider only the n most recent ones

        return queryset


class InteractionLogList(generics.ListAPIView):
    """
        List either all stored interactions or only the `n` most recent
    """
    permission_classes = [IsAdminUser]

    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer

    def get(self, request, n=0, *args, **kwargs):
        int_details = group_interaction_items(self.queryset)
        if int_details:
            if n:
                int_details = int_details[:n]   # consider only the n most recent ones
            return Response(int_details)
        return Response()


class TranslationLogDetail(generics.RetrieveDestroyAPIView):
    """
        get:
            Return all data stored for the translation `id`
        delete:
            Remove the translation `id`
    """
    permission_classes = [IsAdminUser]

    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer


class InteractionLogDetail(generics.RetrieveDestroyAPIView):
    """
        get:
            Return all data stored for the interaction `id`
        delete:
            Remove the interaction `id`
    """
    permission_classes = [IsAdminUser]

    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer

    def get(self, request, int_id):
        interaction_details = get_single_interaction_details(self.queryset, int_id)
        if interaction_details is not None:
            return Response(interaction_details)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, int_id):
        Interaction.objects.filter(interaction_id=int_id).delete()
        return Response(status=status.HTTP_200_OK)


class TranslatorList(APIView):
    """
        List all available translators
    """
    def get(self, request):
        content = {
            "Singe query translation": translators,
            "Interaction support": int_translators
        }

        return Response(content)


class SchemaList(APIView):
    """
        List all available database schemas
    """
    def get(self, request):
        content = list(schemas)

        return Response(content)


class SchemaDetail(APIView):
    """
        List the table names and column names of the schema named `schema_name`
    """
    def get(self, request, schema_name):
        if schema_name in schema_column_names:
            column_names = schema_column_names[schema_name]
            return Response(column_names)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
