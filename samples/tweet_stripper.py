import pandas as pd

def tweet_id_stripper(file,file_out):
    df=pd.read_csv(file)
    df_tweets=df['tweet_id']
    df_tweets.to_csv(file_out,index=False,header=False)
