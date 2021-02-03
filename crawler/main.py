import json
import time
import tweepy
from kafka import KafkaProducer


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Initalize Kafka Producer --------------------------------
bootstrap_servers = ['localhost:9091']
topic_name = 'crawled_tweets'

producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
# ---------------------------------------------------------

# Auth strings --------------------------------------------
api_key = "<TWITTER_API_KEY>"
api_secret = "<TWITTER_API_SECRET>"

access_token = "<TWITTER_ACCESS_TOKEN>"
access_token_secret = "<TWITTER_ACCESS_TOKEN_SECRET>"
# ----------------------------------------------------------

# Authenticate to Twitter ---------------------------------
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
# ---------------------------------------------------------

# Create API object ---------------------------------------
api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
# ----------------------------------------------------------

# Read configurations -------------------------------------
with open("accounts.txt", "r") as f:
    accounts = [item.strip() for item in f.readlines()]

with open("search_terms.txt", "r") as f:
    search_terms = [item.strip() for item in f.readlines()]

with open("sent_tweets.txt", "r") as f:
    sent = set([item.strip() for item in f.readlines()])


# -----------------------------------------------------------

def add_to_kafka(tweet):
    tweet_data = {
        "user": tweet["_json"]["user"]["screen_name"],
        "tweet": tweet["text"],
        "created_at": str(tweet["created_at"])
    }

    tweet_json = json.dumps(tweet_data, ensure_ascii=False)
    if tweet_json not in sent:
        sent.add(tweet_json)
        print(tweet_json)
        producer.send(topic_name, tweet_json.encode("utf8"))
        producer.flush()


try:
    while True:
        print(bcolors.HEADER + "[ + ] Search Crawler Started.")
        for term in search_terms:
            print(bcolors.OKGREEN + "[ + ] Search Key: " + term)
            for tweet in api.search(q=term):
                t = tweet.text.replace('\n', ' ')
                if t not in sent:
                    add_to_kafka(tweet.__dict__)

        print(bcolors.HEADER + "[ + ] User Crawler Started.")
        for user in accounts:
            print(bcolors.OKGREEN + "[ + ] Username: " + user)
            for tweet in api.user_timeline(user):
                t = tweet.text.replace('\n', ' ')
                if t not in sent:
                    add_to_kafka(tweet.__dict__)
        time.sleep(30)
except KeyboardInterrupt as e:
    print("Sent tweets saved")
    with open("sent_tweets.txt", "a") as f:
        f.writelines([item for item in sent])
