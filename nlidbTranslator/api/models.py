from django.db import models

from api.analysis import schemas, translators
from api.setup_util import int_translators

# choices for the CharFields of the django models
TRANSLATOR_CHOICES = list(zip(translators, translators))
INT_TRANSLATOR_CHOICES = list(zip(int_translators, int_translators))
DATABASE_CHOICES = sorted(list(zip(schemas, schemas)))


class Translation(models.Model):
    nl_question = models.CharField(max_length=1000)
    sql_statement = models.CharField(
        max_length=1000,
        editable=False
    )
    db_schema = models.CharField(
        max_length=100,
        choices=DATABASE_CHOICES,
        default=DATABASE_CHOICES[0],
    )
    translator = models.CharField(
        max_length=100,
        choices=TRANSLATOR_CHOICES,
        default=TRANSLATOR_CHOICES[0],
    )
    created = models.DateTimeField(auto_now_add=True)


class Interaction(models.Model):
    interaction_id = models.IntegerField(
        editable=False
    )
    nl_question = models.CharField(max_length=1000)
    sql_statement = models.CharField(
        max_length=1000,
        editable=False
    )
    db_schema = models.CharField(
        max_length=100,
        choices=DATABASE_CHOICES,
        default=DATABASE_CHOICES[0],
    )
    translator = models.CharField(
        max_length=100,
        choices=INT_TRANSLATOR_CHOICES,
        default=INT_TRANSLATOR_CHOICES[0],
    )
    url = models.URLField(
        editable=False
    )
    created = models.DateTimeField(auto_now_add=True)