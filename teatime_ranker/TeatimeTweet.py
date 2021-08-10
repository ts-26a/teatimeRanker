from .util import twid_to_ms, str_today
from .User import User

class TeatimeTweet:
    def __init__(self, tweet_obj, api):
        self.api = api
        self.parse_tweet(tweet_obj)
    
    def parse_tweet(self, tweet):
        self.ms = twid_to_ms(tweet.id) // 1000
        self.author = User(tweet.user.id, self.api)
        self.text = tweet.text
        self.date = str_today()
        self.id = tweet.id
    
    def is_valid_tweet(self):
        return 0 <= self.ms < 6000 and "ティータイムですわ" in self.text