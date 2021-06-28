import argparse
import os
from pathlib import Path
import nltk
from api.paths import TRANSLATORS_DIR, PROJECT_ROOT
from api.adapters.editsql import parse_args_sparc, parse_args_spider
from editsql.data_util.atis_data import ATISDataset
from editsql.preprocess import preprocess


def execute_preprocess(model="spider"):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default=model)
    parser.add_argument('--remove_from', action='store_true', default=True)
    args = parser.parse_args()

    preprocess(args.dataset, args.remove_from)


def execute_run_partially(model="spider"):
    if model == "sparc":
        params = parse_args_sparc.interpret_args()
    else:
        params = parse_args_spider.interpret_args()

    _ = ATISDataset(params)  # just so that all files are generated


if __name__ == '__main__':
    # permanent switch of working directory
    # necessary due to relative import in editsql/data_util
    new_working_dir = Path(TRANSLATORS_DIR) / "editsql"
    os.chdir(str(new_working_dir))

    #download nltk needed modules
    nltk.download('punkt')

    # build spider data
    execute_preprocess("spider")
    execute_run_partially("spider")

    # build sparc data
    execute_preprocess("sparc")
    execute_run_partially("sparc")
