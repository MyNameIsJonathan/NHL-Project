import tweepy
import os
import csv
import pandas as pd
from NHL_scrape_functions import savePickle, KnuthMorrisPratt


explicit_words = [
    'anal', 
    'anus', 
    'arse', 
    'ass', 
    'ballsack', 
    'balls', 
    'bastard', 
    'bitch', 
    'biatch', 
    'bloody', 
    'blowjob', 
    'blow job', 
    'bollock', 
    'bollok', 
    'boner', 
    'boob', 
    'bugger', 
    'bum', 
    'butt', 
    'buttplug',
    'clit', 
    'clitoris', 
    'chode',
    'chodestroker',
    'cock', 
    'coon', 
    'crap', 
    'cunt', 
    'damn',
    'damnit',
    'dammit', 
    'dick', 
    'dildo', 
    'dyke', 
    'fag', 
    'feck', 
    'fellate', 
    'fellatio', 
    'felching', 
    'fuck', 
    'f u c k', 
    'fudgepacker', 
    'fudge packer', 
    'flange', 
    'Goddamn', 
    'God damn', 
    'hell', 
    'homo', 
    'jerk', 
    'jizz', 
    'knobend', 
    'knob end', 
    'labia', 
    'muff', 
    'nigger', 
    'nigga', 
    'penis', 
    'piss', 
    'poop', 
    'prick', 
    'pube', 
    'pussy', 
    'queer', 
    'scrotum', 
    'sex', 
    'shit', 
    's hit', 
    'sh1t', 
    'slut', 
    'smegma', 
    'spunk', 
    'tit', 
    'tosser', 
    'turd', 
    'twat', 
    'vagina', 
    'wank', 
    'whore']

# Get keys and tokens for twitter scrape via tweepy. These are saved in local environment
my_consumer_key = os.environ['my_consumer_key']
my_consumer_secret = os.environ['my_consumer_secret']
my_access_token = os.environ['my_access_token']
my_access_token_secret = os.environ['my_access_token_secret']

# Use tokens and keys for authorization for twitter access
auth = tweepy.OAuthHandler(my_consumer_key, my_consumer_secret)
auth.set_access_token(my_access_token, my_access_token_secret)

# Instantiate the tweepy api instance 
api = tweepy.API(auth, wait_on_rate_limit=True)


# Search twitter for tweets given a key word, saving these tweets in the list 'searched_tweets'
searched_tweets = []
max_tweets = 150 #We want a total of 150 tweets, which will be displayed on the website
last_id = -1 #Start with a null tweet id; incrementing last_id obviates scraping the same tweet multiple times
while len(searched_tweets) < max_tweets: # While we have fewer than the desired number of tweets
    count = max_tweets - len(searched_tweets)
    try: # Watch for tweepy error, otherwise keep scraping
        new_tweets = api.search(q='stamkos', count=count, max_id=str(last_id - 1))
        if not new_tweets: # If we scrape no new tweets before we have our desited number of tweets saved
            break
        for tweet in new_tweets: #
            # Filter out tweets that are retweeted (contain RT or are marked as retweeted) 
            # Filter out tweets that have a swear word contained in the list explicit_words; use Knuth-Morris-Prayy algorithm to improve speed
            contains_swear = False
            if (not tweet.retweeted) and ('RT @' not in tweet.text): # We dont want retweeted tweets, to prevent duplicates
                for swear_word in explicit_words:
                    # Run KnuthMorrisPratt to search for presence of swear words in tweet text
                    # Runs in time O(|pattern| + |text|)
                    # Algorithm adapted from online homework assignment from my Coursera UCSD class on string algos
                    if KnuthMorrisPratt(swear_word, tweet.text):
                        contains_swear = True
                        break
                if contains_swear is False:
                    searched_tweets.append(tweet)
        # Increment tweet id to obviate the inclusion of duplicates
        last_id = new_tweets[-1].id
    except tweepy.TweepError as e:
        # This error could indicate that we have hit maximum twitter API inqueries for the current time period
        print(e)

# Save the list as a pickle file to be retrieved by the routes.py file for the website
savePickle(searched_tweets, f"pickleFiles/stamkosTweets/stamkosTweets_{pd.to_datetime('today').date()}")
