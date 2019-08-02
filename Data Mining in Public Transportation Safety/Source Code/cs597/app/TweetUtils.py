import nltk
import re, random
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


words = set(nltk.corpus.words.words())
porter = PorterStemmer()


stop_words = set(stopwords.words('english'))

def preprocess(tweet):
    
    # Convert to lower case
    tweet = tweet.lower()
    # Replace links with the word URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
    # Replace @username with ""
    tweet = re.sub('@[^\s]+', '', tweet)
    # Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    # Removed punctuation using regex
    #tweet = re.sub(r'[^\w\s]', '', tweet)
    # Removed non-english words
    tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet) if w.lower() in words or not w.isalpha())
    #remove unicodes
    tweet = tweet.encode('ascii', errors='ignore').strip().decode('ascii')
    # Removed stopwords    
    #tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet) if not w in stop_words)
    #stemming of words    
    #tweet = " ".join(porter.stem(word) for word in nltk.wordpunct_tokenize(tweet))
    
    return tweet

#print(preprocess("RT @copenhagenizers: #hgnhl :-) 20 people arrived for a meeting at our office in Copenhagen today. They filled up less than one spot for car parking.\u2026"))



'''
from TweetUtils import preprocess
print(preprocess(tweet))
'''