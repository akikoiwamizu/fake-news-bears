import requests
import os
import json
from tweet_funcs import tweet_id_stripper, username_handler
import time

# Making Directories
print("0. Making Directories")
working_directory = os.getcwd()
twitter_directory = working_directory + "/users_in/"
json_directory = working_directory + "/json_users_out/"

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

print("2. Finished Gathering usernames. Ready for requests")

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# Hardcoded for now, working on google cloud function to replace this
bearer_token = os.popen(
    "curl https://us-central1-fake-news-bears.cloudfunctions.net/secret_twitter"
).read()


def create_url(usernames):
    user_fields = "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,verified_type,withheld"
    # usernames should be comma separated giant string list.
    url = "https://api.twitter.com/2/users/by?usernames={}&user.fields={}".format(
        usernames, user_fields
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
    if response.status_code == 429:
        print("Rate Limittier, pausing for 15 min")
        time.sleep(int(response.headers["Retry-After"]))
    elif response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )
    return response.json()


def main():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    while usernames:
        tweets_100 = usernames[:100]
        users = ",".join(tweets_100)
        url = create_url(users)
        json_response = connect_to_endpoint(url)
        file_out = json_directory + timestr + "_users_" + ".json"
        with open(file_out, "a+") as f:
            data = json.dumps(json_response)
            json.dump(data, f, indent=4, separators=(",", ": "))
            print(f"3. Dumping data to JSON file in json directory. {len(usernames)} Users to go")
        del usernames[:100]
    print(f"4. All Done! data is in {json_directory}")


if __name__ == "__main__":
    main()
