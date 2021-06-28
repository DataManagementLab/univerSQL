from rest_framework import serializers

from api.models import Translation, Interaction


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ["id", "nl_question", "sql_statement", "db_schema", "translator"]


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ["url", "interaction_id", "nl_question", "sql_statement", "db_schema", "translator"]


class UtteranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ["nl_question", "sql_statement"]
