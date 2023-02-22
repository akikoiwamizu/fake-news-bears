from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer
from transformers import AutoConfig
import numpy as np
from scipy.special import softmax
import csv
import urllib.request
import logging as log
import os
from pathlib import Path
import pandas as pd
import time 
import sys

## We make a partition of the dataframe_tweets. We then modify part of it but its' not part of the parent dataframe so this error comes up. This is set to ignore that error since we append to list and it doesn't matter
pd.options.mode.chained_assignment = None 

## Change to INFO or DEBUG for logs.
log.basicConfig(level=log.INFO)

# Tasks:
# emoji, emotion, hate, irony, offensive, sentiment
# stance/abortion, stance/atheism, stance/climate, stance/feminist, stance/hillary
potentialTasks = ['emoji', 'emotion', 'hate' ,'irony', 'offensive', 'sentiment']
if len(sys.argv)<2:
    task = "hate" ##default choice
else:
    task = sys.argv[1]
    if (task in potentialTasks):
        log.info(f"\t Task is a valid choice. Moving on")
    else:
        raise Exception(f"Task is not a valid Task. Choose one of the following: {potentialTasks}")

# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def get_Tokenizer(token_name,task):
    TOKEN_repo = f"{token_name}-{task}"
    FILE_t_repo = f"./model/{TOKEN_repo}"
    log.info("\t Getting Tokenizer as file does not exist")
    tokenizer = AutoTokenizer.from_pretrained(TOKEN_repo,force_download=True)
    tokenizer.save_pretrained(FILE_t_repo) ##Choosing to save token files so that we can reuse when we dockerize and API this setup
    return tokenizer

def get_Model(model_name,task):
    MODEL_repo = f"{model_name}-{task}"
    FILE_m_repo = f"./model/{MODEL_repo}"
    log.info("\t Getting Model as file does not exist")
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_repo,force_download=True)
    model.save_pretrained(FILE_m_repo) ##Choosing to save model files so that we can reuse when we dockerize and API this setup
    return model

def get_Labels(task):
    labels=[]
    mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/{task}/mapping.txt"
    with urllib.request.urlopen(mapping_link) as f:
        html = f.read().decode('utf-8').split("\n")
        csvreader = csv.reader(html, delimiter='\t')
    labels = [row[1] for row in csvreader if len(row) > 1]
    log.debug(f"Labels are {labels}")
    return labels

def get_scoring_list(dataframe,model):
    validateDataFrame(dataframe)
    userPartition = dataframe['author_id'].to_list()
    totalUsers = dataframe['author_id'].nunique()
    scoring_list = []
    time_list=[]
    progress = 0
    for user in userPartition:
        startTime = time.time()
        dataframe_user=dataframe.loc[dataframe['author_id'] == user]
        log.debug(f"\t There are {len(dataframe_user)} text rows to go through for this user")
        encoded_series = dataframe_user['text'].apply(lambda x: tokenizer(x, return_tensors='pt'))
        features = encoded_series.apply(lambda x: model(**x))
        scores = features.apply(lambda x: x[0][0].detach().numpy())
        scores_softmax = scores.apply(lambda x: softmax(x))
        dataframe_user['non-hate'] = scores_softmax.apply(lambda x: x[0])
        non_hate_value = round(dataframe_user['non-hate'].mean(),4) ##For now using mean but can change to median easily
        top_3_btweets = dataframe_user[['non-hate','text']].sort_values(by=['non-hate'], ascending=True).head(3).values.tolist()
        scoring_list.append([user,non_hate_value,top_3_btweets])
        endTime = time.time()
        time_list.append([progress,round((endTime-startTime),3)])
        log.debug(f"\t Scoring List is \n\t {scoring_list}.  \n\t The size of the scoring list is {len(scoring_list)}")
        progress += 1
        log.info(f"\t Finished {progress} users. {totalUsers-progress} users to go")
        log.debug(f"\t Duration of loop is {round((endTime-startTime),3)} seconds.  Previous iterations are {time_list}")
    return scoring_list

def validateDataFrame(dataframe):
    if isinstance(dataframe, pd.DataFrame):
        if {'author_id', 'text'}.issubset(dataframe.columns):
            log.debug('\t Dataframe Validated')
        else:
            raise Exception("Dataframe doesn't have [author_id] or [text] columns. Verify dataframe.columns exist")
    else:
        raise Exception("Object is not DataFrame.  Please pass in valid DataFrame")
    
## Creating Directories
model_dir = os.getcwd() + '/model'
os.makedirs(model_dir, exist_ok=True)
log.debug({model_dir})
## Will make this yargs later on for model directory
roberta_model = model_dir + '/cardiffnlp' + f'/twitter-roberta-base-{task}'
tokenizer_config_file = roberta_model + '/tokenizer_config.json'
model_config_file = roberta_model + '/config.json'
log.debug(f"roberta_model:{roberta_model}")
## Check if Tokenizer file exists. If it does use already solved model and no need to redownload
if Path(tokenizer_config_file).is_file():
    log.info(f"\t Tokenizer File is ready. Loading Token File")
    log.debug(f"\t {tokenizer_config_file}")
    tokenizer = AutoTokenizer.from_pretrained(roberta_model)
else:
    log.info(f"\t Downloading Token files to {roberta_model} directory")
    tokenizer = get_Tokenizer("cardiffnlp/twitter-roberta-base",task)
    
## Check if Model file exists. If it does use already solved model and no need to redownload
if Path(model_config_file).is_file():
    log.info(f"\t Model File is ready. Loading Model File")
    model = AutoModelForSequenceClassification.from_pretrained(roberta_model)
else:
    log.debug(f"\t {Path(model_config_file).is_file()},{model_config_file}")
    log.info(f"\t Downloading Model files to {roberta_model} directory")
    model = get_Model("cardiffnlp/twitter-roberta-base",task)

df_input = pd.read_csv('../samples/data.csv')
result = get_scoring_list(df_input,model)