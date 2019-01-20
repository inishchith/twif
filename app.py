import random
import time

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener

import requests

import config 
from utils import process_tweet, get_gif


TWEET_LENGTH = 200
USERNAME = "imTwif"
BLACKLISTED_IDS = requests.get("https://raw.githubusercontent.com/MikeNGarrett/twitter-blacklist/master/list.json").json()
BACKOFF_TIME = 2

FILE_PATH = "./static/response.gif"
POS_TAGS = ["NNP", "NN", "NNS", "VB"]

# Twitter client
auth = tweepy.OAuthHandler(config.CONSUMER_API, config.CONSUMER_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

class Listener(StreamListener):
    def on_status(self,data):
        tweet_id = data.id
        tweet_text = data.text
        tweet_from = data.user.screen_name

        print(tweet_id,tweet_from,tweet_text)
        mentions, tokens, all_tokens = process_tweet(tweet_text)

        mentions.append(tweet_from)
        mentions.remove(USERNAME)
        mentions = set(mentions)

        print(mentions, tokens)

        tagged_users = ""
        for mention in mentions:
            user = api.get_user(screen_name = mention)
            if user.id not in BLACKLISTED_IDS:
                if len(tagged_users) + len(mention) <= TWEET_LENGTH: 
                    tagged_users += "@" + mention + " "

        print(tagged_users)
        if tagged_users:
            if len(all_tokens) > 2:        
                # Term search .get(1) : NNP -> NN -> NNS -> VB 
            
                found = False
                for tag in POS_TAGS:
                    if tokens.get(tag):
                        found = get_gif(FILE_PATH, tokens[tag][0])
                        if found:
                            if len(tagged_users) +len(tokens[tag][0]) < TWEET_LENGTH :
                                tagged_users += "#" + tokens[tag][0]
                            break
                if not found:
                    get_gif(FILE_PATH,"sorry",n_gifs = 20)
            else:
                print('BIGRAM ')
                get_gif(FILE_PATH," ".join(all_tokens))

            api.update_with_media(status=tagged_users,filename=FILE_PATH,in_reply_to_status_id=tweet_id)
        else:
            api.update_status("Hello darkness my friend.. "+tagged_users)
    
    def on_error(self,status):
        if status == 420:
            print("BACKOFF")
        time.sleep(BACKOFF_TIME)

def print_date_time():
    # tweet out random jokes 
    request_data = requests.get(url)

    # check character limit 

    if request_data.status_code == 200:
        print(request_data.text)
    else:
        # api.update_status("Hello darkness my friend.. "+tagged_users)


scheduler = BackgroundScheduler()
scheduler.add_job(func=print_date_time, trigger="interval", seconds = ) # 86400
scheduler.start()


print("STREAMING.. ")
tweet_stream = Stream(auth = api.auth,listener = Listener())
tweet_stream.filter(track=["@imTwif"])