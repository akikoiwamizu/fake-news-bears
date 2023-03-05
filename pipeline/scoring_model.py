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

## Supress scientific notation for values
pd.set_option("display.float_format", str)

## Change to INFO or DEBUG for logs.
log.basicConfig(level=log.INFO)

# Tasks:
# emoji, emotion, hate, irony, offensive, sentiment
# stance/abortion, stance/atheism, stance/climate, stance/feminist, stance/hillary

## For now only doing 3 ML binary ml models: hate, irony and offensive. Will add more as we see fit.
potentialTasks = ["hate", "irony", "offensive", "all"]
defaultModel = "cardiffnlp/twitter-roberta-base"  ## Choosing this model for this script. Will add other models in different scripts and import base functions from this script
task = sys.argv[1]  ##which task are you looking for
path = sys.argv[2]  ##location of CSV file


def inputValidation(task, path):
    if len(sys.argv) != 3:
        raise Exception("Not enough arguments or Too many Arguments.  Try script again")
        sys.exit(1)
    else:
        log.debug("Arguments are good")
    if task.lower() in potentialTasks:
        log.info(f"\t Task is a valid choice. Moving on")
        task = task.lower()
    else:
        raise Exception(
            f"\t Task is not a valid Task. Choose one of the following: {potentialTasks}"
        )
        sys.exit(1)
    if Path(path).is_file():
        log.info(f"\t CSV file exists. Will Validate later on")
    else:
        raise Exception(
            f"\t {path} is not valid path.\n Please check that csv file exists Script requires Full Path and not relative paths"
        )
        sys.exit(1)
    return task, path


# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = "@user" if t.startswith("@") and len(t) > 1 else t
        t = "http" if t.startswith("http") else t
        new_text.append(t)
    return " ".join(new_text)


def getTasks(task):
    if task == "hate":
        tasks = ["hate"]
    elif task == "offensive":
        tasks = ["offensive"]
    elif task == ["irony"]:
        tasks = "irony"
    else:
        tasks = ["hate", "irony", "offensive"]
    return tasks


## Will make this yargs later on for model directory
## Default choice - twitter-roberta-base
def get_Tokenizer(token_name, task):
    model_dir = os.getcwd() + "/model"
    os.makedirs(model_dir, exist_ok=True)

    TOKEN_repo = f"{token_name}-{task}"
    roberta_model = model_dir + f"/{TOKEN_repo}"
    tokenizer_config_file = roberta_model + "/tokenizer_config.json"

    if Path(tokenizer_config_file).is_file():
        log.info(f"\t Tokenizer File is ready. Loading Token File")
        log.debug(f"\t Token config file:{tokenizer_config_file}")
        tokenizer = AutoTokenizer.from_pretrained(roberta_model)
    else:
        log.info(f"\t Downloading Token files to {roberta_model} directory")
        log.debug(f"\t Model Token file:{tokenizer_config_file}")
        FILE_t_repo = f"./model/{TOKEN_repo}"
        tokenizer = AutoTokenizer.from_pretrained(TOKEN_repo, force_download=True)
        tokenizer.save_pretrained(
            FILE_t_repo
        )  ##Choosing to save token files so that we can reuse when we dockerize and API this setup

    return tokenizer


def get_Model(model_name, task):
    model_dir = os.getcwd() + "/model"
    os.makedirs(model_dir, exist_ok=True)

    MODEL_repo = f"{model_name}-{task}"
    roberta_model = model_dir + f"/{MODEL_repo}"
    model_config_file = roberta_model + "/config.json"

    if Path(model_config_file).is_file():
        log.info(f"\t Model File is ready. Loading Model File")
        model = AutoModelForSequenceClassification.from_pretrained(roberta_model)
    else:
        log.info(f"\t Downloading Model files to {roberta_model} directory")
        FILE_m_repo = f"./model/{MODEL_repo}"
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_repo, force_download=True)
        model.save_pretrained(
            FILE_m_repo
        )  ##Choosing to save model files so that we can reuse when we dockerize and API this setup

    return model


def get_Labels(task):
    labels = []
    mapping_link = (
        f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/{task}/mapping.txt"
    )
    with urllib.request.urlopen(mapping_link) as f:
        html = f.read().decode("utf-8").split("\n")
        csvreader = csv.reader(html, delimiter="\t")
    labels = [row[1] for row in csvreader if len(row) > 1]
    log.debug(f"\t Labels are {labels}")
    return labels


def writeListtoFile(fileList, directory):
    log.debug(f"\t Writing data to file in {directory}")
    with open(rf"{directory}", "w+") as fp:
        for item in fileList:
            fp.write("%s\n" % item)


def readFiletoList(directory):
    fileList = []
    with open(rf"{directory}", "r") as fp:
        for line in fp:
            item = line[:-1]
            fileList.append(item)
    return fileList


def get_scoring_csvs(dataframe, task):
    validateDataFrame(dataframe)
    label = get_Labels(task)[0]
    tokenizer = get_Tokenizer(defaultModel, task)
    model = get_Model(defaultModel, task)

    saveDirectory = os.getcwd() + "/savestate"
    os.makedirs(saveDirectory, exist_ok=True)
    saveFile = saveDirectory + f"/{task}_users.txt"

    if Path(saveFile).is_file():
        log.info(
            f"\t Saved File exists from previous run. Continuing from Saved File in {saveFile}"
        )
        userPartition = readFiletoList(saveFile)
        totalUsers = len(userPartition)
    else:
        log.info(f"\t First time running job for {label}. Save fie is in {saveFile}")
        userPartition = dataframe["author_id"].unique().tolist()
        writeListtoFile(userPartition, saveFile)
        totalUsers = len(userPartition)

    users_directory = os.getcwd() + f"/users_score_{task}/"
    tweets_directory = os.getcwd() + f"/tweets_score_{task}/"
    log.debug(
        f"\t Making Users directory:{users_directory}\n\t Making Tweets directory:{tweets_directory}"
    )
    os.makedirs(users_directory, exist_ok=True)
    os.makedirs(tweets_directory, exist_ok=True)

    time_list = []
    progress = 0

    for user in userPartition:
        user_scoring_list = []
        tweet_scoring_list = []
        userFile = (
            users_directory + "user_" + str(user) + "_" + str.replace(label, "-", "_") + ".csv"
        )
        tweetFile = (
            tweets_directory
            + "tweets_user_"
            + str(user)
            + "_"
            + str.replace(label, "-", "_")
            + ".csv"
        )
        startTime = time.time()

        dataframe_user = dataframe.loc[dataframe["author_id"] == user].astype(
            str
        )  ##Prevent scientific notation
        log.debug(f"\t There are {len(dataframe_user)} text rows to go through for user_id:{user}")
        encoded_series = dataframe_user["text"].apply(lambda x: tokenizer(x, return_tensors="pt"))
        features = encoded_series.apply(lambda x: model(**x))
        scores = features.apply(lambda x: x[0][0].detach().numpy())
        scores_softmax = scores.apply(lambda x: softmax(x))
        dataframe_user[label] = scores_softmax.apply(lambda x: x[0])
        score_value = round(
            dataframe_user[label].mean(), 4
        )  ##For now using mean but can change to median easily
        top_3_btweets = (
            dataframe_user[[label, "text"]]
            .sort_values(by=[label], ascending=True)
            .head(3)
            .values.tolist()
        )
        user_scoring_list.append([user, score_value, top_3_btweets])
        tweet_scoring_list.extend(dataframe_user[["author_id", "id", label]].values.tolist())
        user_output_label = "low_3_" + str.replace(label, "-", "_") + "_tweets"
        user_DF = pd.DataFrame(user_scoring_list, columns=["user_id", label, user_output_label])
        tweet_DF = pd.DataFrame(tweet_scoring_list, columns=["user_id", "tweet_id", label])
        user_DF.to_csv(userFile, encoding="utf-8", index=False)
        tweet_DF.to_csv(tweetFile, encoding="utf-8", index=False)

        with open(saveFile, "r") as fp:  ##Fixing Saved File in case it needs to restart.
            lines = fp.readlines()

        with open(saveFile, "w") as fp:  ##Writing remaining user_ids back in
            for line in lines:
                if line.strip("\n") != str(user):
                    fp.write(line)
                else:
                    log.debug(f"\t removing user {user}")

        endTime = time.time()
        progress += 1
        time_list.append([progress, round((endTime - startTime), 3)])
        log.debug(
            f"\t User Scoring List is \n\t {user_scoring_list}.  \n\t The size of the tweet scoring list is {len(user_scoring_list)}"
        )
        log.debug(
            f"\t Tweet Scoring List is \n\t {tweet_scoring_list}.  \n\t The size of the tweet scoring list is {len(tweet_scoring_list)}"
        )
        log.info(f"\t Finished {progress} users. {totalUsers-progress} users to go")
        log.debug(
            f"\t Duration of loop is {round((endTime-startTime),3)} seconds. Runs so far are {time_list}"
        )
        time.sleep(
            2
        )  ##Throttles CPU to make it manageable.  Encoding step is a ton of CPU cost and theirs no way around it.
    return users_directory, tweets_directory


def validateDataFrame(dataframe):
    if isinstance(dataframe, pd.DataFrame):
        if {"author_id", "text"}.issubset(dataframe.columns):
            log.debug("\t Dataframe Validated")
        else:
            raise Exception(
                "Dataframe doesn't have [author_id] or [text] columns. Verify dataframe.columns exist and rename if necessary"
            )
            sys.exit(1)
    else:
        raise Exception("Object is not DataFrame.  Please pass in valid DataFrame")
        sys.exit(1)


inputValidation(task, path)
df_input = pd.read_csv(f"{path}")
tasks = getTasks(task)
directories = []
for task in tasks:
    users_directory, tweet_directory = get_scoring_csvs(df_input, task)
    log.info(
        f"\t Finished {task}. {task} user files are in {users_directory} and {task} tweet files are in {tweet_directory}"
    )
    directories.extend([users_directory, tweet_directory])

log.info(f"Finished All Tasks! Files are in {directories}")
