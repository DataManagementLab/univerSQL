#!/usr/bin/env bash

GLOVE=translators/glove.42B.300d.txt
TABLE_SCHEMAS=nlidbTranslator/api/schemas/spider_tables.json
BERT_MODEL=translators/editsql/model/bert/data/annotated_wikisql_and_PyTorch_bert_param/pytorch_model_uncased_L-12_H-768_A-12.bin
EDITSQL_SPIDER_PRETRAINED_MODEL=translators/editsql/logs/logs_spider_editsql/save_12
EDITSQL_SPARC_PRETRAINED_MODEL=translators/editsql/logs/logs_sparc_editsql/save_31_sparc_editsql
CONCEPT_NET=translators/IRNet/conceptNet
IRNET_PRETRAINED_MODEL=translators/IRNet/saved_model/IRNet_pretrained.model


pip install --upgrade setuptools wheel gdown

echo -n "Continue with setup for EditSQL and IRNet (recommended)? (y/n) "
read continue_reply
if [[ ${continue_reply} == "n" ]]; then
  echo -n "Delete what is already there for EditSQL and IRNet? (y/n) "
  read delete_reply
  if [[ ${delete_reply} == "y" ]]; then
    echo "Deleting adapter directories for EditSQL and IRNet..."
    rm nlidbTranslator/api/adapters/*
  fi
  echo "Exiting with minimal setup."
  exit
fi


# fetch the submodules
git submodule update --init


# Download needed files:

if [ -f "$GLOVE" ]; then
	echo "$GLOVE exists."
else
  echo "GloVe does not exist. Downloading GloVe ..."
  # Download Glove
  gdown https://nlp.stanford.edu/data/wordvecs/glove.42B.300d.zip -O translators/glove.42B.300d.zip
  unzip translators/glove.42B.300d.zip -d translators/
fi

if [ -f "$TABLE_SCHEMAS" ]; then
	echo "$TABLE_SCHEMAS exists."
else
  echo "spider_tables.json does not exist. Downloading spider tables.json ..."
  # Download Spider, unzip and move tables to correponding directory
  gdown https://drive.google.com/uc?id=11icoH_EA-NYb0OrPTdehRWm_d7-DIzWX
  unzip spider.zip
  mv spider/spider_tables.json $TABLE_SCHEMAS
fi

if [ -f "$BERT_MODEL" ]; then
	echo "$BERT_MODEL exists."
else
	echo "BERT-Model does not exist. Downloading pretrained BERT model ..."
  # Download the pretrained BERT model
  gdown https://drive.google.com/uc?id=1f_LEWVgrtZLRuoiExJa5fNzTS8-WcAX9 -O  translators/editsql/model/bert/data/annotated_wikisql_and_PyTorch_bert_param/pytorch_model_uncased_L-12_H-768_A-12.bin
fi

if [ -f "$EDITSQL_SPIDER_PRETRAINED_MODEL" ]; then
	echo "$EDITSQL_SPIDER_PRETRAINED_MODEL exists."
else
	echo "Trained EditSQL-Model for Spider does not exist. Downloading trained model ..."
  # Download the trained model for Spider and put it under logs/logs_spider_editsql/save_12.
  gdown https://drive.google.com/uc?id=1KwXIdJBYKG0-PzCi1GvvSnUxJzxNq_CL -O translators/editsql/logs/logs_spider_editsql/
fi

if [ -f "$EDITSQL_SPARC_PRETRAINED_MODEL" ]; then
	echo "$EDITSQL_SPARC_PRETRAINED_MODEL exists."
else
  echo "Trained EditSQL-Model for Sparc does not exist. Downloading trained model ..."
  # Download the trained model for SParC and put it under logs/logs_sparc_editsql/save_31_sparc_editsql.
  gdown  https://drive.google.com/uc?id=1MRN3_mklw8biUphFxmD7OXJ57yS-FkJP -O translators/editsql/logs/logs_sparc_editsql/
fi

if [ -d "$CONCEPT_NET" ]; then
	echo "$CONCEPT_NET exists."
else
	echo "ConceptNet does not exist. Downloading ConceptNet ..."
  # Download and unzip conceptNet
  gdown https://drive.google.com/uc?id=1LgyjtDmf3Xd1txwq8HwKD6d6VJj5pLmn -O  translators/IRNet/
  unzip translators/IRNet/conceptNet.zip -d translators/IRNet/
fi

if [ -f "$IRNET_PRETRAINED_MODEL" ]; then
	echo "$IRNET_PRETRAINED_MODEL exists."
else
	echo "IRNet trained Model does not exist. Downloading trained model ..."
  # Download IRNet pretrained model
  mkdir translators/IRNet/saved_model
  gdown https://drive.google.com/uc?id=1VoV28fneYss8HaZmoThGlvYU3A-aK31q -O $IRNET_PRETRAINED_MODEL
fi


