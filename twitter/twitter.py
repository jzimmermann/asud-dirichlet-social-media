import os.path
import json
import csv
import re

import requests

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from requests.auth import AuthBase
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords

# constants
# api
stream_url = "https://api.twitter.com/labs/1/tweets/stream/sample"
consumer_key = "8reoM2s2OkLexoXsvKRVQxVEO"  # Add your API key here
consumer_secret = "U90Pi6hUGl53hfOOINZdXO14siCzI5h53sOVweJIMmVEwgihL0"  # Add your API secret key here

# program

# message filters
# length
max_message_length = 280
message_length_threshold = 0.2
min_message_length = max_message_length * message_length_threshold

# language(s)
included_languages = ['en']

# stop words
# nltk.download()
stop_words = stopwords.words('english')
stop_words.append('RT')

tweet_tokenizer = TweetTokenizer()


# Gets a bearer token
class BearerTokenAuth(AuthBase):
    def __init__(self, consumer_key, consumer_secret):
        self.bearer_token_url = "https://api.twitter.com/oauth2/token"
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.bearer_token = self.get_bearer_token()

    def get_bearer_token(self):
        response = requests.post(
            self.bearer_token_url,
            auth=(self.consumer_key, self.consumer_secret),
            data={'grant_type': 'client_credentials'},
            headers={"User-Agent": "TwitterDevSampledStreamQuickStartPython"})

        if response.status_code != 200:
            raise Exception(f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

        body = response.json()
        return body['access_token']

    def __call__(self, r):
        r.headers['Authorization'] = f"Bearer %s" % self.bearer_token
        return r


def stream_connect(auth):
    response = requests.get(stream_url,
                            auth=auth,
                            headers={"User-Agent": "TwitterDevSampledStreamQuickStartPython"},
                            stream=True)
    is_file = os.path.isfile("tweets.csv")
    f = open("tweets.csv", "a")
    writer = csv.writer(f)
    if not is_file:
        writer.writerow(['created_at', 'text', 'lang'])

    for response_line in response.iter_lines():
        if response_line:
            json_data = json.loads(response_line)
            row = create_row(json_data)
            if validate_row(row):
                writer.writerow(row)


def create_row(json_data):
    created_at = json_data['data']['created_at']
    text = determine_text(json_data)
    lang = determine_language(text)
    return [created_at, text, lang]


def determine_text(json_data):
    text = json_data['data']['text']
    text = remove_mentions(text)
    tokens = tweet_tokenizer.tokenize(text)

    filtered_tokens = []
    for token in tokens:
        if token not in stop_words:
            filtered_tokens.append(token)

    return ' '.join(filtered_tokens)


def remove_mentions(text):
    return re.sub(r"(?:\@|https?\://)\S+", "", text)


def determine_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'unknown'


def validate_language(lang):
    try:
        included_languages.index(lang)
        return True
    except ValueError:
        return False


def validate_text(text):
    if len(text) < min_message_length:
        return False
    else:
        return True


def validate_row(row):
    valid = True
    valid = valid & validate_text(row[1])
    valid = valid & validate_language(row[2])
    return valid


bearer_token = BearerTokenAuth(consumer_key, consumer_secret)

# Listen to the stream. This reconnection logic will attempt to reconnect as soon as a disconnection is detected.
while True:
    stream_connect(bearer_token)
