try:
    import json
except ImportError:
    import simplejson as json

#Import the necessary methods from "twitter" library
from twitter import OAuth, TwitterStream
import SentiWordsSentence

import re
import time
import datetime

from twitter_passwords import ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET #import authorisation passwords

locations = ['ireland', 'antrim', 'armagh', 'carlow', 'cavan', 'clare', 'cork', 'derry', 'donegal', 'down', 'dublin', 'fermanagh', 'galway', 'kerry', 'kildare', 'kilkenny', 'laois', 'leitrim', 'limerick', 'longford', 'louth', 'mayo', 'meath', 'monaghan', 'offaly', 'roscommon', 'sligo', 'tipperary', 'tyrone', 'waterford', 'westmeath', 'wexford', 'wicklow']
sleep_time = 1

#extracts user location from json dump
def find_tweet_location(d):
    if "retweeted_status" in d:
        if "user" in d["retweeted_status"]:
            if "location" in d["retweeted_status"]["user"]:
                return add_tweet_location(d["retweeted_status"]["user"]["location"])

    elif "quoted_status" in d:
        if "user" in d["quoted_status"]:
            if "location" in d["quoted_status"]["user"]:
                return add_tweet_location(d["quoted_status"]["user"]["location"])

    elif "user" in d:
        if "location" in d["user"]:
            return add_tweet_location(d["user"]["location"])

#returns location to be added to json file - want information about demographic in ireland
def add_tweet_location(locat):

    if locat is None:
        return "null"

    locat = re.sub("[^a-zA-Z ]", "", locat)
    locat = locat.split(" ")

    for dest in locat:
        if dest.lower() in locations:
            return dest.lower()
        else:
            continue

    return "other"

# Apply timestamp as unique id name
def make_id():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime("%Y%m%d%H%M%S%f")
    id_name = ["data/", st, ".json"]
    return "".join(id_name)

#finds the full text of the tweet and extracts it
def get_full_text(data):

    if "retweeted_status" in data:
        if "quoted_status" in data["retweeted_status"]:
            if "extended_tweet" in data["retweeted_status"]["quoted_status"]:
                if "full_text" in data["retweeted_status"]["quoted_status"]["extended_tweet"]:
                    return data["retweeted_status"]["quoted_status"]["extended_tweet"]["full_text"]

        elif "extended_tweet" in data["retweeted_status"]:
            if "full_text" in data["retweeted_status"]["extended_tweet"]:
                return data["retweeted_status"]["extended_tweet"]["full_text"]

    elif "quoted_status" in data:
        if "extended_tweet" in data["quoted_status"]:
            if "full_text" in data["quoted_status"]["extended_tweet"]:
                return data["quoted_status"]["extended_tweet"]["full_text"]

    elif "extended_tweet" in data:
        if "full_text" in data["extended_tweet"]:
            return data["extended_tweet"]["full_text"]


    return None


def main():

    # Variables that contains the user credentials to access Twitter API
    oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    # Initiate the connection to Twitter Streaming API
    twitter_stream = TwitterStream(auth=oauth)

    # scraping tweets the contain one ore more of the words that we are tracking
    iterator = twitter_stream.statuses.filter(track="eighthamendment, 8thAmendment, repealthe8th, repealtheeighth, 8thRef, 1thing4choice, realityofrepeal, time4choice, savethe8th, savetheeighth, save8Rally, rally4life, strike4repeal, riseandrepeal, right2life", language="en")

    for tweet in iterator:

        JSONdata = json.dumps(tweet)

        if "full_text" in JSONdata: #Only looks at tweets that have full text in it

            text = get_full_text(tweet) #extracts the full text in the json file

            if text is not None: #As long as the full_text was found

                json_id = make_id() #create a unique timestamp id

                with open(json_id, "w+") as f: #give it its own file for the whole json data
                    json.dump(tweet, f)

                data = json.load(open(json_id))  #load the json data

                location = find_tweet_location(data) # get the tweet location
                location = str(location) #turn it into a string

                #writes tweet id num, actual tweet text, user location and sentiment analysis score to a master file
                with open("data/all_tweets.json", "a+") as fi:
                    fi.write(json_id + " ")

                    json.dump(text, fi)
                    sentenceAlph = re.sub("[^a-zA-Z ]", "", text) #removes anything that is not a letter
                    score = str(round(SentiWordsSentence.sentTweetWords_final_score(sentenceAlph), 2)) #get the sentiment analysis score and round it to 2 decimal places
                    fi.write(" " + location + " " + score + "\n")


        time.sleep(sleep_time) #reduces chances of rate limiting

if __name__ == "__main__":
    main()