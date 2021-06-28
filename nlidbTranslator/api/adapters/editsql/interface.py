from adapters.editsql.editsql_adapter import EditsqlAdapter
from api.setup_util import no_stdout

ediAdapter_spider = None
ediAdapter_sparc = None


@no_stdout
def setup():
    global ediAdapter_spider, ediAdapter_sparc
    ediAdapter_spider = EditsqlAdapter("spider")
    ediAdapter_sparc = EditsqlAdapter("sparc")


@no_stdout
def translate(nl_question, db_id):
    return ediAdapter_spider.translate(nl_question, db_id)


@no_stdout
def translate_interaction(nl_question, db_id, prev_nl_questions, prev_predictions):
    return ediAdapter_sparc.translate_interaction(nl_question, db_id, prev_nl_questions, prev_predictions)