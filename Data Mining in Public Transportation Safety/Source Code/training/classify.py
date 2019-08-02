import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tflearn
import tensorflow as tf
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

start = time.time()
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

    # remove unicodes
    tweet = tweet.encode('ascii', errors='ignore').strip().decode('ascii')

    # Removed stopwords
    tweet = " ".join(w for w in nltk.wordpunct_tokenize(
        tweet) if not w in stop_words)

    # stemming of words
    tweet = " ".join(porter.stem(word)
                     for word in nltk.wordpunct_tokenize(tweet))

    return tweet


data = None

# read the json file and load the training data
with open('data.json') as json_data:
    data = json.load(json_data)
    # print(data)

# get a list of all categories to train for
categories = list(data.keys())

words = []
# a list of tuples with words in the sentence and category name
docs = []

for each_category in data.keys():
    for each_sentence in data[each_category]:
        # remove any punctuation from the sentence
        each_sentence = remove_punctuation(each_sentence)
        print(each_sentence)
        # extract words from each sentence and append to the word list
        w = nltk.word_tokenize(each_sentence)
        print("tokenized words: ", w)
        words.extend(w)
        docs.append((w, each_category))

# stem and lower each word and remove duplicates
words = [stemmer.stem(w.lower()) for w in words]
words = sorted(list(set(words)))

# print(words)
# print(docs)

# create our training data
training = []
output = []
# create an empty array for our output
output_empty = [0] * len(categories)


for doc in docs:
    # initialize our bag of words(bow) for each document in the list
    bow = []
    # list of tokenized words for the pattern
    token_words = doc[0]
    # stem each word
    token_words = [stemmer.stem(word.lower()) for word in token_words]
    # create our bag of words array
    for w in words:
        bow.append(1) if w in token_words else bow.append(0)

    output_row = list(output_empty)
    output_row[categories.index(doc[1])] = 1

    # our training set will contain a the bag of words model and the output row that tells
    # which catefory that bow belongs to.
    training.append([bow, output_row])

# shuffle our features and turn into np.array as tensorflow  takes in numpy array
random.shuffle(training)
training = np.array(training)

# trainX contains the Bag of words and train_y contains the label/ category
train_x = list(training[:, 0])
train_y = list(training[:, 1])

# reset underlying graph data
tf.reset_default_graph()
# Build neural network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
# Start training (apply gradient descent algorithm)
print("------------------------->" + str(len(train_x[0])))
model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
model.save('model.tflearn')

end = time.time()
print("TRAINING TIME = %s seconds" % (end - start))
print(10 * "\n")

# let's test the mdodel for a few sentences:
# the first two sentences are used for training, and the last two sentences are not present in the training data.
sent_1 = "hulk training to keep bus safe . k9"  # pos
sent_2 = "Employ automated speed enforcement cameras."  # pos
sent_3 = "is telling to throw under the bus to . bbcan7"  # unk
sent_4 = "i mean i got a bus ticket so we just figure out the other logistics"  # neu
sent_5 = "alert & ; strong thunderstorm near railroad moving ne at 55 . small hail , wind over 35 are possible ."  # neg

# a method that takes in a sentence and list of all words
# and returns the data in a form the can be fed to tensorflow


def get_tf_record(sentence):
    global words
    # tokenize the pattern
    sentence = preprocess(sentence)
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


# we can start to predict the results for each of the 4 sentences
print(categories[np.argmax(model.predict([get_tf_record(sent_1)]))])
print(categories[np.argmax(model.predict([get_tf_record(sent_2)]))])
print(categories[np.argmax(model.predict([get_tf_record(sent_3)]))])
print(categories[np.argmax(model.predict([get_tf_record(sent_4)]))])
print(categories[np.argmax(model.predict([get_tf_record(sent_5)]))])
