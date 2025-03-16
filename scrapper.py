from tweety import Twitter  
import pandas as pd  
from langdetect import detect  
from textblob import TextBlob

async def load_tweets(usr):
    app = Twitter("session")
    tweets = await app.get_tweets(username=usr,wait_time=2)
    
    tweet_list = []  
    for tweet in tweets:
        if hasattr(tweet, "text"):
            text = tweet.text
            try:
                if detect(text) == "en": 
                    tweet_list.append(text)
            except:
                continue  

    return pd.DataFrame({"tweets": tweet_list})


def analyze_sentiment(text):
    polarity = TextBlob(text.strip().lower()).sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"
