import requests
import os
import json
from tweet_stripper import tweet_id_stripper
import time

#Making Directories
print("0. Making Directories")
working_directory=os.getcwd()
twitter_directory='tweets_in/'
twitter_out_directory='tweets_out/'
json_directory='json_out/'

cmd_tod = "mkdir {0}/{1}".format(working_directory,twitter_out_directory)
cmd_jd = "mkdir {0}/{1}".format(working_directory,json_directory)
os.system(cmd_tod)
os.system(cmd_jd)

#Getting Twitter ID files
print("1. Grabbing Twitter Files with tweet_id in them")
tweet_files=os.listdir(twitter_directory)
tweet_files.remove('.DS_Store')
for file in tweet_files:
    file_d=twitter_directory+file
    file_out=twitter_out_directory+file[:-4]+"out"+".csv"
    tweet_id_stripper(file_d,file_out)
print("2. Finished Gathering input files. Ready for requests")
tweet_id_files=os.listdir(twitter_out_directory)
try:
    tweet_id_files.remove('.DS_Store')
except ValueError:
    print("\t No DS_Store file found.  Continuing")
# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
#Hardcoded for now, working on google cloud function to replace this
bearer_token = "ENTER IN BEARER AUTH TOKEN"

def create_url(ids):
    tweet_fields = "tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,source,text,withheld"
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    # You can adjust ids to include a single Tweets.
    url = "https://api.twitter.com/2/tweets?ids={}&{}".format(
        ids, tweet_fields)
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
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    for file in tweet_id_files:
        i=0
        file=twitter_out_directory+file
        with open(file,"r") as f:
            lines = f.read().splitlines()
            i+=1
        while lines:
            tweets_100=lines[:100]
            ids=','.join(tweets_100)
            url = create_url(ids)
            json_response = connect_to_endpoint(url)
            file_out=json_directory+timestr+'_tweets_'+str(i)+'.json'
            with open(file_out, 'a+') as f:
                data=json.dumps(json_response)
                json.dump(data,f,indent=4,separators=(',',': '))
                print("3. Dumping data to JSON file in json directory")
            del lines[:100]

        


if __name__ == "__main__":
    main()
