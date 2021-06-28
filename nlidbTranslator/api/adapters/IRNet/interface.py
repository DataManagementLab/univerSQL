from adapters.IRNet.irnet_adapter import IRNetAdapter
from api.setup_util import no_stdout

iRNetAdapter = None


@no_stdout
def setup():
    global iRNetAdapter
    iRNetAdapter = IRNetAdapter()


@no_stdout
def translate(nl_question, db_id):
    return iRNetAdapter.translate(nl_question, db_id)
