import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import random
import json
import string
import unicodedata
import sys
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import time
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# a table structure to hold the different punctuation used
tbl = dict.fromkeys(i for i in range(sys.maxunicode)
                    if unicodedata.category(chr(i)).startswith('P'))


words = set(nltk.corpus.words.words())

porter = PorterStemmer()

stop_words = set(stopwords.words('english'))

# method to remove punctuations from sentences.
def remove_punctuation(text):
    return text.translate(tbl)

# initialize the stemmer
stemmer = LancasterStemmer()
# variable to hold the Json data read from the file

def preprocess(tweet):
   
    # Convert to lower case
    tweet = tweet.lower()

    # Replace links with the word URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)

    # Replace @username with ""
    #tweet = re.sub('@[^\s]+', '', tweet)

    # Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)

    # Removed punctuation using regex
    tweet = re.sub(r'[^\w\s]', '', tweet)

    # Removed non-english words
    #tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet) if w.lower() in words or not w.isalpha())

    #remove unicodes
    tweet = tweet.encode('ascii', errors='ignore').strip().decode('ascii')

    # Removed stopwords    
    tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet) if not w in stop_words)

    #stemming of words    
    tweet = " ".join(porter.stem(word) for word in nltk.wordpunct_tokenize(tweet))
    
    return tweet
