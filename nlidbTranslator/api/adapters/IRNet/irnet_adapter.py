import pickle
import nltk
import numpy as np
import torch
import os
import copy

from IRNet.preprocess import utils
from src.rule import semQL
from api.adapters.IRNet.constants import PATH_TO_CONCEPTNET
from api.paths import SCHEMAS_DIR
from api.setup_util import schemas, no_stdout
from IRNet.sem2SQL import transform
from .parse_args import init_arg_parser
from IRNet.src.models.model import IRNet
from IRNet.src.rule.sem_utils import wordnet_lemmatizer
from IRNet.src.utils import to_batch_seq
from api import setup_util


class IRNetAdapter:
    def __init__(self):
        self.params = init_arg_parser()
        self.params.schemas_dir = SCHEMAS_DIR

        # load model
        grammar = semQL.Grammar()
        self.model = IRNet(self.params, grammar)
        if self.params.cuda:
            self.model.cuda()
            pretrained_model = torch.load(self.params.load_model, map_location=lambda storage, loc: storage)
        else:
            pretrained_model = torch.load(self.params.load_model, map_location='cpu')

        pretrained_modeled = copy.deepcopy(pretrained_model)
        for k in pretrained_model.keys():
            if k not in self.model.state_dict().keys():
                del pretrained_modeled[k]

        self.model.load_state_dict(pretrained_modeled)

        #   load glove
        self.model.word_emb = setup_util.glove_embeddings

        # load table data
        self.schemas = schemas

    def epoch_acc(self, batch_size, sql_data, table_data, beam_size=3):
        self.model.eval()
        sql_data_list = []
        sql_data_list.append(sql_data)
        perm = list(range(len(sql_data_list)))
        examples = to_batch_seq(sql_data_list, self.schemas, perm, 0, len(perm),
                                is_train=False)
        example = examples[0]
        results_all = self.model.parse(example, beam_size=beam_size)
        results = results_all[0]
        list_preds = []
        try:
            pred = " ".join([str(x) for x in results[0].actions])
            for x in results:
                list_preds.append(" ".join(str(x.actions)))
        except Exception as e:
            pred = ""

        pre_sql = example.sql_json['pre_sql']
        pre_sql['sketch_result'] = " ".join(str(x) for x in results_all[1])
        pre_sql['model_result'] = pred
        return pre_sql

    def preprocessData(self, data, schema):
        with open(os.path.join(PATH_TO_CONCEPTNET, 'english_RelatedTo.pkl'), 'rb') as f:
            english_RelatedTo = pickle.load(f)

        with open(os.path.join(PATH_TO_CONCEPTNET, 'english_IsA.pkl'), 'rb') as f:
            english_IsA = pickle.load(f)

        # copy of the origin question_toks
        data["origin_question_toks"] = data["question_toks"]
        data['question_toks'] = utils.symbol_filter(data['question_toks'])
        origin_question_toks = utils.symbol_filter([x for x in data['origin_question_toks'] if x.lower() != 'the'])
        question_toks = [wordnet_lemmatizer.lemmatize(x.lower()) for x in data['question_toks'] if x.lower() != 'the']
        data['question_toks'] = question_toks
        header_toks = []
        header_toks_list = []

        num_toks = len(question_toks)
        idx = 0
        tok_concol = []
        type_concol = []
        nltk_result = nltk.pos_tag(question_toks)

        while idx < num_toks:

            # fully header
            end_idx, header = utils.fully_part_header(question_toks, idx, num_toks, header_toks)
            if header:
                tok_concol.append(question_toks[idx: end_idx])
                type_concol.append(["col"])
                idx = end_idx
                continue

            # check for table
            end_idx, tname = utils.group_header(question_toks, idx, num_toks, schema['table_names'])
            if tname:
                tok_concol.append(question_toks[idx: end_idx])
                type_concol.append(["table"])
                idx = end_idx
                continue

            # check for column
            end_idx, header = utils.group_header(question_toks, idx, num_toks, header_toks)
            if header:
                tok_concol.append(question_toks[idx: end_idx])
                type_concol.append(["col"])
                idx = end_idx
                continue

            # check for partial column
            end_idx, tname = utils.partial_header(question_toks, idx, header_toks_list)
            if tname:
                tok_concol.append(tname)
                type_concol.append(["col"])
                idx = end_idx
                continue

            # check for aggregation
            end_idx, agg = utils.group_header(question_toks, idx, num_toks, utils.AGG)
            if agg:
                tok_concol.append(question_toks[idx: end_idx])
                type_concol.append(["agg"])
                idx = end_idx
                continue

            if nltk_result[idx][1] == 'RBR' or nltk_result[idx][1] == 'JJR':
                tok_concol.append([question_toks[idx]])
                type_concol.append(['MORE'])
                idx += 1
                continue

            if nltk_result[idx][1] == 'RBS' or nltk_result[idx][1] == 'JJS':
                tok_concol.append([question_toks[idx]])
                type_concol.append(['MOST'])
                idx += 1
                continue

            # string match for Time Format
            if utils.num2year(question_toks[idx]):
                question_toks[idx] = 'year'
                end_idx, header = utils.group_header(question_toks, idx, num_toks, header_toks)
                if header:
                    tok_concol.append(question_toks[idx: end_idx])
                    type_concol.append(["col"])
                    idx = end_idx
                    continue

            def get_concept_result(toks, graph):
                for begin_id in range(0, len(toks)):
                    for r_ind in reversed(range(1, len(toks) + 1 - begin_id)):
                        tmp_query = "_".join(toks[begin_id:r_ind])
                        if tmp_query in graph:
                            mi = graph[tmp_query]
                            for col in data['col_set']:
                                if col in mi:
                                    return col

            end_idx, symbol = utils.group_symbol(question_toks, idx, num_toks)
            if symbol:
                tmp_toks = [x for x in question_toks[idx: end_idx]]
                assert len(tmp_toks) > 0, print(symbol, question_toks)
                pro_result = get_concept_result(tmp_toks, english_IsA)
                if pro_result is None:
                    pro_result = get_concept_result(tmp_toks, english_RelatedTo)
                if pro_result is None:
                    pro_result = "NONE"
                for tmp in tmp_toks:
                    tok_concol.append([tmp])
                    type_concol.append([pro_result])
                    pro_result = "NONE"
                idx = end_idx
                continue

            end_idx, values = utils.group_values(origin_question_toks, idx, num_toks)
            if values and (len(values) > 1 or question_toks[idx - 1] not in ['?', '.']):
                tmp_toks = [wordnet_lemmatizer.lemmatize(x) for x in question_toks[idx: end_idx] if x.isalnum() is True]
                assert len(tmp_toks) > 0, print(question_toks[idx: end_idx], values, question_toks, idx, end_idx)
                pro_result = get_concept_result(tmp_toks, english_IsA)
                if pro_result is None:
                    pro_result = get_concept_result(tmp_toks, english_RelatedTo)
                if pro_result is None:
                    pro_result = "NONE"
                for tmp in tmp_toks:
                    tok_concol.append([tmp])
                    type_concol.append([pro_result])
                    pro_result = "NONE"
                idx = end_idx
                continue

            result = utils.group_digital(question_toks, idx)
            if result is True:
                tok_concol.append(question_toks[idx: idx + 1])
                type_concol.append(["value"])
                idx += 1
                continue
            if question_toks[idx] == ['ha']:
                question_toks[idx] = ['have']

            tok_concol.append([question_toks[idx]])
            type_concol.append(['NONE'])
            idx += 1
            continue

        data['question_arg'] = tok_concol
        data['question_arg_type'] = type_concol
        data['nltk_pos'] = nltk_result

        return data

    @no_stdout
    def translate(self, nl_question, db_id):
        data = self.createSqlData(nl_question, db_id)
        schema = self.schemas[data['db_id']]
        myArray = np.asarray(schema['column_names'])
        data['col_set'] = myArray[:, 1].tolist()
        data['table_names'] = schema['table_names']
        processData = self.preprocessData(data, schema)
        list = []
        list.append(processData)
        result = self.epoch_acc(1, processData, schema)
        result['model_result_replace'] = result['model_result']

        processedResult = transform(result, schema)
        print(processedResult)
        return processedResult[0]

    def createSqlData(self, nl_question, db_id):
        nl_question = nl_question.replace(" .", ".")
        nl_question = nl_question.replace(" !", "!")
        nl_question = nl_question.replace(" ?", "?")

        data = {}
        data['db_id'] = db_id
        data['question'] = nl_question
        data['query'] = ''
        question_tokens = data['question']
        question_tokens = question_tokens.split()
        question_tokens.append(question_tokens[-1][-1])
        question_tokens[-2] = question_tokens[-2][:-1]
        data["question_toks"] = question_tokens
        return data
