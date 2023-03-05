# 20230205-142915_tweets_user_5558312.json

# removes all the backslash (\) characters behind quotes
# loads the output as JSON
# removes the first data element
# serializes the JSON into a utf-8 text json file

# there are some unicode letters within the ascii such as \u2026
import re
import math
import os
import fnmatch
import json

from charset_normalizer import CharsetNormalizerMatches as CnM

encoding = (
    CnM.from_path("samples/json_users_out/20230205-143622_users_.json").best().first().encoding
)
print(f"encoding is: {encoding}")

# create sub directory "json_clean_tweets"
OUT_DIR = os.getcwd() + "/samples/json_clean_tweets"
OUT_FILE = OUT_DIR + "/usa_congress_tweets.json"
FILES_TO_COMBINE = 500

IN_DIR = os.getcwd() + "/samples/json_tweets_out"
file_names = fnmatch.filter(os.listdir(IN_DIR), "*.*")
num_files = len(file_names)

division = num_files / FILES_TO_COMBINE
num_batches = math.floor(division)
stragglers = math.ceil((division - num_batches) * FILES_TO_COMBINE)

print(f"Current dir: {os.getcwd()}")
print(f"Source dir:  {IN_DIR}")
print(f"Output dir:  {OUT_DIR}")

print(f"File name: {file_names[0]}")
print(f"File Count: {num_files}")

print(
    f"batches: {num_batches}, stragglers: {stragglers}, total files: {FILES_TO_COMBINE*num_batches + stragglers}"
)


# open the raw input file and create a new file that does not contain badly escaped data
# such as backslashed quotes e.g. replace \" with just "
# write nice BigQuery friendly JSON
def clean_tweets_write_json(IN_FILE, outfile):

    with open(IN_FILE, "r") as infile:

        print(f"Opened file: {IN_FILE}")
        for line in infile:
            # replace all instances of \" with instances of "
            line = re.sub(r'(\\")', '"', line)

            # replaces instance of \\"KC\\" with \"KC\" or \\"some stuff here\\" with \"some stuff here\"
            line = re.sub(r'(\\\\")', '\\"', line)

            # remove the very first quote and the last quote in the file, i.e. "{ .... }" should be { .... } per JSON standards
            line = re.sub(r"^.|.$", "", line)

            json_obj = json.loads(line)

            # if file does not contain data then skip it
            if "data" not in json_obj.keys():
                return

            data_list = json_obj["data"]

            for x in range(0, len(data_list)):
                s = json.dumps(data_list[x])

                # write one line of json (without an ending comma)
                # this formats the data correctly for BigQuery ingestion
                outfile.write(s + "\n")


# create OUT_DIR if it doesn't exist
if os.path.exists(OUT_DIR) == False:
    os.mkdir(OUT_DIR)

# open file in write mode and overwrite since this is our first time
with open(OUT_FILE, "w") as outfile:

    for i in range(0, num_batches):
        print(f"processing batch# {i}")

        # combine file numbers from start to end indexes
        start_idx = FILES_TO_COMBINE * i
        end_idx = start_idx + FILES_TO_COMBINE

        for j in range(start_idx, end_idx):

            # overwrite the file if this is the first time we are opening it

            clean_tweets_write_json(IN_DIR + "/" + file_names[j], outfile)

    if stragglers > 0:

        start_idx = FILES_TO_COMBINE * num_batches
        end_idx = len(file_names)

        for j in range(start_idx, end_idx):
            print(f"processing straggler# {j}")
            clean_tweets_write_json(IN_DIR + "/" + file_names[j], outfile)
