import tweepy
import os
import csv
import pandas as pd
from NHL_scrape_functions import savePickle


my_consumer_key = os.environ['my_consumer_key']
my_consumer_secret = os.environ['my_consumer_secret']
my_access_token = os.environ['my_access_token']
my_access_token_secret = os.environ['my_access_token_secret']

auth = tweepy.OAuthHandler(my_consumer_key, my_consumer_secret)
auth.set_access_token(my_access_token, my_access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

searched_tweets = []
max_tweets = 150
last_id = -1
while len(searched_tweets) < max_tweets:
    count = max_tweets - len(searched_tweets)
    try:
        new_tweets = api.search(q='stamkos', count=count, max_id=str(last_id - 1))
        if not new_tweets:
            break
        for tweet in new_tweets:
            if (not tweet.retweeted) and ('RT @' not in tweet.text):
                searched_tweets.append(tweet)
        last_id = new_tweets[-1].id
    except tweepy.TweepError as e:
        print(e)

savePickle(searched_tweets, f"pickleFiles/stamkosTweets/stamkosTweets_{pd.to_datetime('today').date()}")