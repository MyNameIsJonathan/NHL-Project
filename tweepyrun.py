import tweepy
import os
import string
import pandas as pd
from sqlalchemy import create_engine
import NHL_scrape_functions as nhl
from flasksite.config import Config



# engine = create_engine(f'mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}')

def scrapeTweets():

    """[ Scrapes 150 tweets mentioning 'Stamkos' using the Tweepy library to access the Twitter API ]

    Returns:
        [ list ] -- [ a list of 150 tweets. Each tweet is of type: tweepy.models.Status ]
    """

    # Create a list of explicit words to look for
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
                if (not tweet.retweeted) and ('RT @' not in tweet.text) and (nhl.KnuthMorrisPratt('stamkos', tweet.text.lower())): # We dont want retweeted tweets, to prevent duplicates
                    for swear_word in explicit_words:
                        # Run KnuthMorrisPratt to search for presence of swear words in tweet text
                        # Runs in time O(|pattern| + |text|)
                        # Algorithm adapted from online homework assignment from my Coursera UCSD class on string algos
                        if nhl.KnuthMorrisPratt(swear_word, tweet.text):
                            contains_swear = True
                            break
                    if contains_swear is False:
                        searched_tweets.append(tweet)
            # Increment tweet id to obviate the inclusion of duplicates
            last_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # This error could indicate that we have hit maximum twitter API inqueries for the current time period
            print(e)

    return searched_tweets

def saveTweetsinDB(tweets, engine):

    """[ Saves the provided tweets in the MySQL database, overwriting previous tweets in the DB. Does not return. ]"""

    # Create a set of printable characters. Will be used to filter text and users
    printable = set(string.printable)

    # Create an empty pandas DF with the necessary columns and labels
    mycols = ['created_at', 'text', 'user']
    tweetdf = pd.DataFrame(columns=mycols)
    tweetdf.index.name = 'Tweet ID'

    # Loop through tweets, filtering out Author's name, non-printable characters. Append resulting Series to tweetdf.
    for tweet in tweets:
        currentTweet = tweet._json
        currentTweet['text'] = ''.join(filter(lambda x: x in printable, currentTweet['text']))
        currentTweet['user'] = currentTweet['user']['screen_name']
        myseries = pd.Series(list(currentTweet.values()), index=list(tweet._json.keys()), name=tweet.id)
        myseries = myseries.drop([i for i in myseries.index if not i in mycols])
        tweetdf = tweetdf.append(myseries)

    # Make the created_at column a datetime.date dtype
    tweetdf['created_at'] = pd.to_datetime(tweetdf['created_at']).dt.date

    # Submit tweetdf to MySQL DB
    tweetdf.to_sql(
        name='stamkosTweets',
        con=engine,
        index=False,
        if_exists='replace')

def openTweets(engine):

    """[ Use the provided SQLAlchemy engine to access tweets of Stamkos ]

    Returns:
        [ Pandas.DataFrame ] -- [ returns a Pandas.DataFrame of the tweets' time, text, and author name ]
    """

    sqltweets = pd.read_sql_table("stamkosTweets", engine)

    return sqltweets



if __name__ == '__main__':
    engine = nhl.nonFlaskCreateEngine()
    myTweets = scrapeTweets()
    saveTweetsinDB(myTweets, engine)
