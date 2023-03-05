import requests
import os
import json
from tweet_funcs import tweet_id_stripper, username_handler
import time

# Making Directories
print("0. Making Directories")
working_directory = os.getcwd()
twitter_directory = working_directory + "/users_in/"
json_directory = working_directory + "/json_tweets_out/"
user_ids = []

cmd_jd = "mkdir {0}".format(json_directory)
os.system(cmd_jd)

# Getting Twitter User files
print("1. Grabbing Twitter Users with username in them")
tweet_files = os.listdir(twitter_directory)
try:
    tweet_files.remove(".DS_Store")
except ValueError:
    print("\t No DS_Store file found.  Continuing")
usernames = []
for file in tweet_files:
    file = twitter_directory + file
    usernames.extend(username_handler(file))

print("2. Finished Gathering usernames. Preparing user_ids from usernames")


# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# Hardcoded for now, working on google cloud function to replace this
bearer_token = os.popen(
    "curl https://us-central1-fake-news-bears.cloudfunctions.net/secret_twitter"
).read()


def create_userids(usernames):
    while usernames:
        users_100 = usernames[
            :100
        ]  ##Twitter only lets you look at 100 user_ids at a time so have to batch them up
        usernames_string = ",".join(users_100)
        # usernames should be comma separated giant string list. Output
        url = "https://api.twitter.com/2/users/by?usernames={}".format(usernames_string)
        response = requests.request("GET", url, auth=bearer_oauth)
        data = response.json()
        for i in range(len(users_100)):
            try:
                id_value = data["data"][i]["id"]
                user_ids.extend([id_value])
            except:
                continue
        del usernames[:100]
    return user_ids


def create_url(userid):
    tweet_fields = "tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,source,text,withheld"
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    # You can adjust ids to include a single Tweets.
    url = "https://api.twitter.com/2/users/{}/tweets?max_results=100&{}".format(
        userid, tweet_fields
    )
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2TweetLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth)
    # print(response.status_code)
    if response.status_code == 400:
        print("user_id not found")
    elif response.status_code == 429:
        print("Rate Limittier, pausing for 15 min")
        time.sleep(int(response.headers["Retry-After"]))
    elif response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )
    return response.json()


def main():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    user_ids = create_userids(usernames)
    for userid in list(user_ids):
        url = create_url(userid)
        json_response = connect_to_endpoint(url)
        file_out = (
            json_directory + timestr + "_tweets_user_" + str(userid) + ".json"
        )  ##Dumped by user_id, will join with Bigquery users table to see the actual user later on
        with open(file_out, "a+") as f:
            data = json.dumps(json_response)
            json.dump(data, f, indent=4, separators=(",", ": "))
            print(f"3. Dumping data to JSON file in json directory. {len(user_ids)} Users to go")
        user_ids.remove(userid)
    print(f"All Done! Tweet Data is located in {json_directory}")


if __name__ == "__main__":
    main()
