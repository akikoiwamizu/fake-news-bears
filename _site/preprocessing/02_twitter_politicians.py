# GCS Bucket: fake_news_bears_politics


# read house posts CSV file
# separate tweet id, created at, politician handle
# convert it to bigquery friendly JSON
# save the JSON

import os
import re
import json
import sys
import pandas as pd
from charset_normalizer import CharsetNormalizerMatches as CnM


# input file names
CSV_FILE_SENATE = "us_politicians_twitter_2023/us_senate_posts_2022_2023.csv"
CSV_FILE_HOUSE = "us_politicians_twitter_2023/us_house_posts_2022_2023.csv"

# output file nnames
JSON_FILE_HOUSE = "us_politicians_twitter_2023/02_us_house_posts_for_bquery_2023.json"
JSON_FILE_SENATE = "us_politicians_twitter_2023/02_us_senate_posts_for_bquery_2023.json"

# find all digits \d+ closest to end of string $
pattern_tweet_id = re.compile("\d+$")

# find all urls in the middle of text
pattern_url = re.compile(
    "\\b((?:https?|ftp|file)://[-a-zA-Z0-9+&@#/%?=~_|!:, .;]*[-a-zA-Z0-9+&@#/%=~_|])"
)

# debugs
encoding = CnM.from_path(CSV_FILE_SENATE).best().first().encoding
print(f"Senate file encoding is: {encoding}")
encoding = CnM.from_path(CSV_FILE_HOUSE).best().first().encoding
print(f"House file encoding is: {encoding}")


def processDataFrame(df, runTweetIdPattern=True):
    print(f"processDataFrame: shape is {df.shape}")

    # rename column names to make them readable
    df.rename(columns={"Source": "tweet_id"}, inplace=True)
    df.rename(columns={"Organization Name": "name"}, inplace=True)
    df.rename(columns={"Username": "username"}, inplace=True)
    df.rename(columns={"Address": "state"}, inplace=True)
    df.rename(columns={"Created": "created_at"}, inplace=True)
    df.rename(columns={"Hashtags": "hashtags"}, inplace=True)
    df.rename(columns={"Homepage": "homepage"}, inplace=True)
    df.rename(columns={"Text": "text"}, inplace=True)
    df.drop(columns=["Org Type", "EIN", "Post Type"], inplace=True)

    df.drop_duplicates(subset=["tweet_id"], inplace=True)

    # drop line that has "Organization Name" as the "name", this is an issue with the data in the file
    df.query("name != 'Organization Name'", inplace=True)

    if runTweetIdPattern == True:
        # get tweet id - regex search returns matched numbers in the group object, we take the first value ie url in the group [0]
        df["tweet_id"] = [
            re.search(pattern_tweet_id, str(x))[0] for x in df["tweet_id"]
        ]

    # extract and save url from text column
    df["url"] = df["text"].str.extract(pattern_url)[0]

    # remove urls from the text column
    df["text"] = df["text"].str.replace(pattern_url, "")

    return df


def writeDataFrame(df, outputfile):
    print(f"writeDataFrame: shape is {df.shape}, output file is: {outputfile}")

    # convert dataframe to json string
    result = df.to_json(orient="records")

    # convert json string to json object (actually a list)
    json_obj = json.loads(result)

    with open(outputfile, "w", encoding="utf-8") as outfile:
        for i in range(0, len(json_obj)):
            s = json.dumps(json_obj[i])

            # write one line of json (without an ending comma), this formats the data correctly for BigQuery ingestion
            outfile.write(s + "\n")

    return


# process and write senate files
df_senate = pd.read_csv(CSV_FILE_SENATE)
df_senate = processDataFrame(df_senate, True)
writeDataFrame(df_senate, JSON_FILE_SENATE)

# process and write house files
df_house = pd.read_csv(CSV_FILE_HOUSE)
df_house = processDataFrame(df_house, False)
writeDataFrame(df_house, JSON_FILE_HOUSE)
