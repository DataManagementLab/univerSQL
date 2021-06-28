# Usage

## Overview of API endpoints

### Information
| Endpoint | Method | Action |
|--------|----|----------|
| `/translators` | GET | list all available models   
| `/schemas` | GET | list all available schemas
| `/schemas/{schema_name}` | GET | list tables and column names for the schema with name `schema_name`

### Translate & Interact
| Endpoint | Required Values | Method | Action |
|-------|---|----|----------|
| `/translate` | `"nl_question", "db_schema", "translator"` | POST | translate a single question
| `/interaction` | `"nl_question", "db_schema", "translator"` |POST | start an interaction
| `/interaction/{int_id}` | `"nl_question"` |POST | add to the existing interaction with id `int_id`

### Logging
| Endpoint | Method | Action |
|--------|----|----------|
| `/translate/logs` | GET | list the logs of all single translations
| `/translate/log_item/{id}` | GET, DELETE | get or delete the single translations with id `id`
| `/interaction/logs` | GET |  list the logs of all interactions
| `/interaction/log_item/{int_id}` | GET, DELETE | get or delete the interaction with id `int_id`


## Usage Scenario
This section presents a possible usage with multiple steps and therefore multiple API calls.

#### 1. Get Information
Look what translators are available using `/translators`
```
{
  "Singe query translation": [
    "IRNet",
    "editsql"
  ],
  "Interaction support": [
    "editsql"
  ]
}
```

Decide on one of the schemas from `/schemas`
```
[
  ...
  "movie_1",
  "network_1",
  "poker_player",
  "program_share",
  "aircraft",
  ...
]
```

#### 2. Request a single translation
Prompt the user to ask a question and sent the following in a POST to `/translate`:
```
{
  "nl_question": "Return the average earnings across all poker players.", 
  "db_schema": "poker_player",
  "translator": "IRNet"
}
```
The system will return a dictionary like this:
```
{
  "id": 0,
  "nl_question": "Return the average earnings across all poker players.",
  "sql_statement": "SELECT AVG (Earnings) FROM poker_player",
  "db_schema": "poker_player",
  "translator": "IRNet"
}
```

#### 3. Inspect the logs
Now have a look at the logs: `/translate/logs`
```
[
    {
      "id": 0,
      "nl_question": "Return the average earnings across all poker players.",
      "sql_statement": "SELECT AVG (Earnings) FROM poker_player",
      "db_schema": "poker_player",
      "translator": "IRNet"
    }
]
```
In this case a list with just the one item for the request above is returned.

#### 4. Conduct an interaction
Prompt the user to ask a question, but this time send a POST to `/interaction` with values:
```
{
  "nl_question": "What is the birth date of each poker player?", 
  "db_schema": "poker_player",
  "translator": "editsql"
}
```
_Caution: Not every system must support interactions! See `/translators` for candidates._

The system will return something similar to:
```
{
    "url": "SERVER_ADDR/interaction/0",
    "interaction_id": 0,
    "nl_question": "What is the birth date of each poker player?",
    "sql_statement": "SELECT Birth_Date FROM people",
    "db_schema": "poker_player",
    "translator": "editsql"
}
```

So far no difference in the procedure...

... but you can now use `/interaction/0` to add a question to this interaction.
To do this, send a POST with values:
```
{
    "nl_question": "Sort the list by the poker player's earnings."
}
```

And you will receive the following:
```
{
    "url": "SERVER_ADDR/interaction/0",
    "interaction_id": 0,
    "translator": "editsql",
    "db_schema": "poker_player",
    "interaction": [
        {
            "nl_question": "What is the birth date of each poker player?",
            "sql_statement": "SELECT Birth_Date FROM people"
        },
        {
            "nl_question": "Sort the list by the poker player's earnings.",
            "sql_statement": "SELECT T1.Birth_Date FROM people AS T1 JOIN poker_player AS T2 ON T1.People_ID = T2.People_ID ORDER BY T2.Earnings"
        }
    ]
}
```
(This is by the way the same output you would get with `/interaction/log_item/0`)

As you can see, the translation is not only based on the current question, but also on the previous ones.

The output also explains why you don't need to specify a database schema nor a translator:
Because they are already set for this interaction with id `0`.
