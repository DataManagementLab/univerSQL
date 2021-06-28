import random
import time
from pathlib import Path

import numpy as np
import json
import torch

from editsql.data_util import atis_batch
from editsql.data_util.atis_data import ATISDataset
from editsql.data_util.interaction import load_function
from editsql.model import model, utils_bert
from editsql.model.schema_interaction_model import SchemaInteractionATISModel
from editsql.postprocess_eval import postprocess_one
from editsql.preprocess import read_database_schema
from editsql.model.bert import tokenization as tokenization
from editsql.model.bert.modeling import BertConfig, BertModel

from adapters.editsql import parse_args_spider, parse_args_sparc
from adapters.editsql.constants import *
from api import setup_util
from api.paths import DB_SCHEMAS_FILE


class EditsqlAdapter:
    """
    Uses the functionality of editsql to translate arbitrary questions into sql
    """

    def __init__(self, model="spider"):
        if model == "sparc":
            params = parse_args_sparc.interpret_args()
        else:
            params = parse_args_spider.interpret_args()

        # create the dataset and model
        data = ATISDataset(params)
        self.model = self.load_model(params, data)

        _, _, self.database_schemas = read_database_schema(DB_SCHEMAS_FILE, schema_tokens={}, column_names={}, database_schemas_dict={})

        # function used for loading of interaction in raw state
        self.int_load_function = load_function(params,
                                               data.entities_dictionary,
                                               data.anonymizer,
                                               database_schema=self.database_schemas)

    def load_model(self, params, data):
        """
        Loads the editsql translation model

        Args:
            params: the parsed arguments
            data: the ATISDataset

        Returns:
            the loaded SchemaInteractionATISModel

        """

        model = SchemaInteractionATISModel(
            params,
            data.input_vocabulary,
            data.output_vocabulary,
            data.output_vocabulary_schema,
            data.anonymizer if params.anonymize and params.anonymization_scoring else None)

        model.load_state_dict(torch.load(params.save_file,map_location='cpu'))
        print("Loaded model from file " + params.save_file)
        model.eval()

        return model

    def prepare_interaction(self, nl_questions, db_id, prev_predictions):
        """
        Creates an InteractionItem that contains the natural language question and the database id

        Args:
            nl_questions: the natural language questions
            db_id: the database that acts as context
            prev_predictions: the previous predictions

        Returns:
            an InteractionItem that contains the natural language question and the database id

        """

        # establish the structure of an interaction in raw state
        example = dict()
        example["final"] = dict()
        example["interaction"] = []

        # fill the general fields
        example["id"] = "dummy id"
        example["scenario"] = ""
        example["interaction_id"] = 42

        # fill the content fields
        example["database_id"] = db_id

        prev_predictions.append("dummy sql query")

        for i, nl_q in enumerate(nl_questions):
            sql_int = [(prev_predictions[i].split(), [])]

            example["interaction"].append({"utterance": nl_q, "sql": sql_int})

        example["final"]["utterance"] = nl_questions[-1]
        example["final"]["sql"] = "query to be predicted"

        # transform the raw interaction to an InteractionItem
        obj, _ = self.int_load_function(example)
        interaction = atis_batch.InteractionItem(obj)

        return interaction

    def translate(self, nl_question, db_id):
        """
        Translate a single natural language question into sql

        Args:
            nl_question: the natural language question
            db_id: the database that acts as context

        Returns:
            the sql prediction

        """

        # preprocess
        nl_questions = [nl_question]
        interaction = self.prepare_interaction(nl_questions, db_id, prev_predictions=[])

        prediction = self.predict(interaction)
        return self.post_process(prediction, db_id)

    def translate_interaction(self, nl_question, db_id, prev_nl_questions, prev_predictions):
        """
        Predict the sql for the next utterance in an interaction

        Args:
            nl_question: the natural language question
            db_id: the database that acts as context
            prev_nl_questions: the previous questions or an empty list
            prev_predictions: the previous predictions or an empty list

        Returns:
            the sql prediction

        """

        # preprocess
        nl_questions = prev_nl_questions + [nl_question]
        interaction = self.prepare_interaction(nl_questions, db_id, prev_predictions)

        prediction = self.predict(interaction)
        return self.post_process(prediction, db_id)

    def predict(self, interaction):
        prediction = self.model.predict_with_predicted_queries(interaction, 1000)
        pred_tokens_raw = prediction[-1][0]
        pred_tokens = pred_tokens_raw[:-1]  # strip the _EOS symbol
        pred_str = " ".join(pred_tokens)
        return pred_str

    def post_process(self, prediction, db_id):
        schema = self.database_schemas[db_id]
        post_processed = postprocess_one(prediction, schema)
        return post_processed

    # ------------ Evaluation -----------------
    def evaluate(self, amount=0, randomness=False, show_all=False, use_gold_query=False):
        """
        Evaluate the translation output of EditsqlAdapter.
        By default the prediction results of standalone editsql act as the reference.
        The use_gold_query switch enables comparison with the gold queries from spider

        Args:
            amount: the amount of samples to use
            randomness: randomly choose samples
            show_all: write all samples, not only those with errors
            use_gold_query: comparison with the gold queries from spider instead of the prediction results of standalone editsql

        """

        # load the prediction results of standalone editsql
        with open(EVAL_REFERENCE_FILE) as infile:
            references = json.load(infile)

        if not amount:
            # let amount default to _all_ examples from the file
            amount = len(references)

        # determine the instances to test on
        if randomness:
            sample_indices = random.sample(range(len(references)), k=amount)
        else:
            sample_indices = range(amount)

        comparisons = []
        num_errors = 0

        start = time.time()
        for i in sample_indices:
            db_id = references[i]["database_id"]
            in_seq_raw = references[i]["input_seq"]
            in_seq = " ".join(in_seq_raw)

            schema = self.database_schemas[db_id]

            dev_prediction_raw = references[i]["flat_prediction"]
            dev_prediction = " ".join(dev_prediction_raw)
            dev_prediction = postprocess_one(dev_prediction, schema)

            translation = self.translate(in_seq, db_id)

            gold = " ".join(references[i]["gold_query"])
            gold = postprocess_one(gold, schema)

            # normalize and prevent numbering from distorting the results
            gold_norm = ''.join("0" if c.isdigit() else c.lower() for c in gold)
            dev_pred_norm = ''.join("0" if c.isdigit() else c.lower() for c in dev_prediction)
            translation_norm = ''.join("0" if c.isdigit() else c.lower() for c in translation)

            if use_gold_query:
                is_error = translation_norm != gold_norm
            else:
                is_error = translation_norm != dev_pred_norm

            if is_error:
                num_errors += 1
            if is_error or show_all:
                comparison = dict()
                comparison["identifier"] = references[i]["identifier"]
                comparison["is_equal"] = not is_error
                comparison["input_seq"] = in_seq
                comparison["prediction"] = {}
                if use_gold_query:
                    comparison["prediction"]["gold       "] = gold
                else:
                    comparison["prediction"]["editsql    "] = dev_prediction
                comparison["prediction"]["translation"] = translation

                comparisons.append(comparison)

        end = time.time()
        duration = end - start
        time_per_item = duration / amount

        num_correct = amount - num_errors
        accuracy = num_correct * 100 / amount

        eval_output = dict()
        eval_output["time per item"] = time_per_item
        eval_output["# items"] = amount
        eval_output["% equal"] = accuracy
        if show_all:
            eval_output["content"] = comparisons
        else:
            eval_output["diff"] = comparisons

        write_json_log_results(eval_output, CURRENT_DIR / "evaluation/results")

    # ------------ Batch processing -----------------
    @classmethod
    def batch_translate(cls, input_file=BATCH_INPUT_FILE, output_dir=BATCH_OUTPUT_DIR):
        """
        Read the list of dicts with values for nl_question and db_id from the input file
        and save the translations to a file in the output directory

        Args:
            input_file: path of file with list of dicts with values for nl_question and db_id
            output_dir: path of dir where the translations are saved

        """

        edi_adap = EditsqlAdapter()

        with open(input_file) as f:
            requests = json.load(f)

        for i, request in enumerate(requests):
            request["sql"] = edi_adap.translate(request["nl_question"], request["db_id"])

        write_json_log_results(requests, output_dir)


def write_json_log_results(content, directory):
    path = Path(directory)

    filename = time.strftime("%Y_%m_%d-%H_%M_%S") + ".json"
    with open(str(path / filename), 'w') as outfile:
        json.dump(content, outfile, indent=4)


# define a modified embeddings loading function that makes use of the preloaded glove
def load_word_embeddings_for_editsql(input_vocabulary, output_vocabulary, output_vocabulary_schema, params):
    glove_embedding_size = 300

    # ------- use preloaded glove -----------
    glove_embeddings = setup_util.glove_embeddings
    # ---------------------------------------

    input_embedding_size = glove_embedding_size

    def create_word_embeddings(vocab):
        vocabulary_embeddings = np.zeros((len(vocab), glove_embedding_size), dtype=np.float32)
        vocabulary_tokens = vocab.inorder_tokens

        glove_oov = 0
        para_oov = 0
        for token in vocabulary_tokens:
            token_id = vocab.token_to_id(token)
            if token in glove_embeddings:
                vocabulary_embeddings[token_id][:glove_embedding_size] = glove_embeddings[token]
            else:
                glove_oov += 1

        print('Glove OOV:', glove_oov, 'Para OOV', para_oov, 'Total', len(vocab))

        return vocabulary_embeddings

    input_vocabulary_embeddings = create_word_embeddings(input_vocabulary)
    output_vocabulary_embeddings = create_word_embeddings(output_vocabulary)
    output_vocabulary_schema_embeddings = None
    if output_vocabulary_schema:
        output_vocabulary_schema_embeddings = create_word_embeddings(output_vocabulary_schema)

    return input_vocabulary_embeddings, output_vocabulary_embeddings, output_vocabulary_schema_embeddings, input_embedding_size


# overwrite the original embeddings loading function with the modified version
model.load_word_embeddings = load_word_embeddings_for_editsql


# define a modified version with absolute path instead of relative path in the first line
def get_bert(params):
    BERT_PT_PATH = str(TRANSLATORS_DIR / "editsql/model/bert/data/annotated_wikisql_and_PyTorch_bert_param")
    map_bert_type_abb = {'uS': 'uncased_L-12_H-768_A-12',
                         'uL': 'uncased_L-24_H-1024_A-16',
                         'cS': 'cased_L-12_H-768_A-12',
                         'cL': 'cased_L-24_H-1024_A-16',
                         'mcS': 'multi_cased_L-12_H-768_A-12'}
    bert_type = map_bert_type_abb[params.bert_type_abb]
    if params.bert_type_abb == 'cS' or params.bert_type_abb == 'cL' or params.bert_type_abb == 'mcS':
        do_lower_case = False
    else:
        do_lower_case = True
    no_pretraining = False

    bert_config_file = os.path.join(BERT_PT_PATH, f'bert_config_{bert_type}.json')
    vocab_file = os.path.join(BERT_PT_PATH, f'vocab_{bert_type}.txt')
    init_checkpoint = os.path.join(BERT_PT_PATH, f'pytorch_model_{bert_type}.bin')

    print('bert_config_file', bert_config_file)
    print('vocab_file', vocab_file)
    print('init_checkpoint', init_checkpoint)

    bert_config = BertConfig.from_json_file(bert_config_file)
    tokenizer = tokenization.FullTokenizer(
        vocab_file=vocab_file, do_lower_case=do_lower_case)
    bert_config.print_status()

    model_bert = BertModel(bert_config)
    if no_pretraining:
        pass
    else:
        model_bert.load_state_dict(torch.load(init_checkpoint, map_location='cpu'))
        print("Load pre-trained parameters.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_bert.to(device)

    return model_bert, tokenizer, bert_config


# overwrite the original function with the modified version
utils_bert.get_bert = get_bert
