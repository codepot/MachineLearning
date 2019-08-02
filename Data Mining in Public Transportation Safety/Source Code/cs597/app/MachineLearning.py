import nltk
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import string
import unicodedata
import sys
import re


import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

words = set(nltk.corpus.words.words())
porter = PorterStemmer()
stop_words = set(stopwords.words('english'))

# a table structure to hold the different punctuation used
tbl = dict.fromkeys(i for i in range(sys.maxunicode)
                    if unicodedata.category(chr(i)).startswith('P'))


# method to remove punctuations from sentences.
def remove_punctuation(text):
    return text.translate(tbl)


# initialize the stemmer
stemmer = LancasterStemmer()


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

    # remove unicodes
    tweet = tweet.encode('ascii', errors='ignore').strip().decode('ascii')

    # Removed stopwords
    tweet = " ".join(w for w in nltk.wordpunct_tokenize(
        tweet) if not w in stop_words)

    # stemming of words
    tweet = " ".join(porter.stem(word)
                     for word in nltk.wordpunct_tokenize(tweet))

    return tweet


# variable to hold the Json data read from the file
data = None


# read the json file and load the training data
with open('app/data.json') as json_data:
    data = json.load(json_data)


# get a list of all categories to train for
categories = list(data.keys())

words = []
# a list of tuples with words in the sentence and category name
docs = []

for each_category in data.keys():
    for each_sentence in data[each_category]:
        # -----------------------------------  PRE-PROCESS THE SENTENCE HERE ------------------------- each_sentence
        # remove any punctuation from the sentence
        each_sentence = remove_punctuation(each_sentence)

        # extract words from each sentence and append to the word list
        w = nltk.word_tokenize(each_sentence)

        words.extend(w)
        docs.append((w, each_category))

# stem and lower each word and remove duplicates
words = [stemmer.stem(w.lower()) for w in words]
words = sorted(list(set(words)))


def get_tf_record(sentence):
    global words
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    # bag of words
    bow = [0]*len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bow[i] = 1

    return(np.array(bow))


# reset underlying graph data
tf.reset_default_graph()
# Build neural network
net = tflearn.input_data(shape=[None, 10677])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 4, activation='softmax')
net = tflearn.regression(net)
model = tflearn.DNN(net, tensorboard_dir='app/tflearn_logs')
# load our saved model
model.load('app/model.tflearn')


def predict(tweet):
    # return categories[np.argmax(model.predict([get_tf_record(preprocess(tweet)]))]
    refined_tweet = preprocess(tweet)
    return categories[np.argmax(model.predict([get_tf_record(refined_tweet)]))]
