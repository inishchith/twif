import random
import time

import requests
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from nltk import ngrams
import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener

import config
from utils import process_tweet, get_gif

TWEET_LENGTH = 240      # - GIF size
USERNAME = "imTwiif"
BLACKLISTED_IDS = requests.get("https://raw.githubusercontent.com/MikeNGarrett/twitter-blacklist/master/list.json").json()
BACKOFF_TIME = 2

FILE_PATH = "./static/response.gif"
POS_TAGS = ["NNP", "NN", "NNS", "VB"]

auth = tweepy.OAuthHandler(config.CONSUMER_API, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


class Listener(StreamListener):

    def on_status(self, tweet):
        tweetId = tweet.id
        tweetText = tweet.text
        tweetFrom = tweet.user.screen_name

        mentions, all_tokens = process_tweet(tweetText)

        mentions.append(tweetFrom)
        if USERNAME in mentions:
            mentions.remove(USERNAME)
        elif USERNAME.lower() in mentions:
            mentions.remove(USERNAME.lower())
        mentions = set(mentions)

        tagged_users = ""
        for mention in mentions:
            user = api.get_user(screen_name=mention)
            if user.id not in BLACKLISTED_IDS:
                if len(tagged_users) + len(mention) <= TWEET_LENGTH:
                    tagged_users += "@" + mention + " "

        print(tagged_users, all_tokens)
        if tagged_users:
            if len(all_tokens) > 2:
                # Term search .get(1) : NNP -> NN -> NNS -> VB

                two_grams = list(ngrams(all_tokens, 2))
                # three_grams = list(ngrams(all_tokens, 3))
                found = False
                print(two_grams)

                for gram in two_grams:
                    token = " ".join(gram)
                    found = get_gif(FILE_PATH, token)
                    if found:
                        # if len(tagged_users) + len(token) < TWEET_LENGTH:
                        #     tagged_users += "#" + tokens[tag][0]
                        break    

                # Still not :()
                if not found:
                    get_gif(FILE_PATH, "sorry", n_gifs=20)
            else:
                get_gif(FILE_PATH, " ".join(all_tokens))

            print(tagged_users)
            api.update_with_media(status=tagged_users, 
                                  filename=FILE_PATH, 
                                  in_reply_to_status_id=tweetId)
        else:
            api.update_status("Hello darkness my friend.. " + tagged_users)

    def on_error(self, status):
        if status == 420:
            print("BACKOFF")
        time.sleep(BACKOFF_TIME)

def joke_trigger():
    url = "https://raw.githubusercontent.com/inishchith/twif/master/static/jokes.json?token=ATShOSKywCsd-2NsBlRuuu2RlKtq2X-Lks5cTZ5fwA%3D%3D"
    request_data = requests.get(url)

    if request_data.status_code == 200:
        jokes = request_data.json()
        n_jokes = len(jokes)
        pick = random.randint(0, n_jokes - 1)
        joke, handle, tag = jokes[pick]["joke"], jokes[pick]["twitter_handle"], jokes[pick]["tag"]

        response_tweet = joke
        if handle and (len(joke) + len(handle) <= TWEET_LENGTH):
            response_tweet += " - " + handle
        elif len(joke) > TWEET_LENGTH:
            response_tweet = joke[:240] + "..." + " - " + handle
        
        if tag:
            get_gif(FILE_PATH, tag)
            api.update_with_media(status=response_tweet, 
                                  filename=FILE_PATH)
        else:
            api.update_status(response_tweet)

    else:
        api.update_status("GitHub be like cats ..")

scheduler = BackgroundScheduler()
scheduler.add_job(func=joke_trigger, 
                  trigger="interval", 
                  seconds=3600)
scheduler.start()

print("STREAMING.. ")
tweet_stream = Stream(auth=api.auth, listener=Listener())
tweet_stream.filter(track=["@imTwiif"])
