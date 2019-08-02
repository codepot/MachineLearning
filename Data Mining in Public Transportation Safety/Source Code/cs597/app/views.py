# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.conf import settings
from .models import sTweet, City
from django.views.generic import CreateView
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from uszipcode import SearchEngine
from geopy.geocoders import Nominatim
import random
import datetime
import csv
import tweepy
import requests
from app.MachineLearning import predict
from django.core import serializers
from django.db.models import Count
from django.db import connection
from uszipcode import Zipcode



consumer_key = 'MJI521gjNHmMUDswLmQsVaqoB'
consumer_secret = 'QnsRBuzifdwBZr3n0RiYkthkmh1bTQNSJmR1aAy7HAGWnDibBV'
access_token = '1097222435806445568-s01bXw3aW78cguAdye3LXS9ylYPhXn'
access_secret = '6TD7JFnzSZqIetsFvVFQWyBWotvhI52Z7kzRK5gHYImRA'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=False)
#api = tweepy.API(auth)


# set simple_zipcode=False to use rich info database
search = SearchEngine(simple_zipcode=True)

signals = {
    "pos": "Safe",
    "neg": "Unsafe",
    "neu": "Neutral",
    "unk": "Unknown"
}

# for testing purpose : MAP VIEW
def gernerate_geo_locations():
    # Longitude of Los Angeles: -118.243685, Latitude of Los Angeles: 34.052234
    tweets = sTweet.objects.all()
    #ran = random.uniform(-0.3, 0.3)
    index = 0
    for tweet in tweets:
        if (index % 7) == 0:
            tweet.longitude = -118.243685+random.uniform(-0.1, 1.6)
            tweet.latitude = 34.352234 + random.uniform(-0.9, 0.3)
        else:
            tweet.longitude = None
            tweet.latitude = None
        tweet.save()    
        index = index + 1
    print("updated")

# Home Page
class Home(CreateView):
    model = City
    #gernerate_geo_locations()
    template_name = 'app/home.html'
    fields = ('zip',)


# handle search form on home page
def Search(request):
    query = request.POST['zipcode']
    radius = request.POST['radius']
    print("" + query + " within " + radius)
    return render(request, "app/tweets.html", {'query_zip': query, 'radius': radius})

def truncate_table():
    cursor = connection.cursor()
    cursor.execute("delete from sqlite_sequence where name='app_stweet'")


def Tweets(request):
    return render(request, "app/tweets.html", {})


# for AJAX calling
@csrf_exempt
def DownloadTweets(request):    
    zip_info = request.GET.get('zip_info')
    radius = request.GET.get('radius_info')
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    zipcode = geolocator.geocode(zip_info)
    address = zipcode.address
    lng = zipcode.latitude
    lat = zipcode.longitude
    request.session['zipcode'] = zip_info
    request.session['address'] = address

    request.session['lng'] = lng
    request.session['lat'] = lat
    geo_query = str(lng)+","+str(lat)

    if(radius != "unlimited"):
        geo_query += ","+radius

    result = ""

    if(radius == "unlimited"):        
        tweets = tweepy.Cursor(api.search, q='bus OR train -filter:retweets', lang='en').items(2000)             
        sTweet.objects.all().delete()
        truncate_table()
        for tweet in tweets:            
            prediction = predict(tweet.text)           
            result += "<tr style='font-family:Verdana; font-size:18px;'><td>" + \
                signals[prediction]+"</td><td>" + tweet.text+"</td><td><img src='/static/image/bullets/" + \
                prediction+".png' height='10' width='10'></td></tr>"
            saveTweet(tweet, prediction, address, lng, lat)

    else:
        tweets = tweepy.Cursor(api.search, q='bus OR train -filter:retweets',
                               geocode="'+geo_query+'", lang='en').items(2000)
        sTweet.objects.all().delete()
        truncate_table()
        for tweet in tweets:
            prediction = predict(tweet.text)
            result += "<tr style='font-family:Verdana; font-size:18px;'><td>" + \
                signals[prediction]+"</td><td>" + tweet.text+"</td><td><img src='/static/image/bullets/" + \
                prediction+".png' height='10' width='10'></td></tr>"
            saveTweet(tweet, prediction, address, lng, lat)
    return JsonResponse(result, safe=False)

def location(lng, lat):
    search = SearchEngine(simple_zipcode=True)    
    res = search.by_coordinates(lng, lat, radius=5000, returns=1)
    if(len(res)==0): return "unknown location" #out of USA
    return res[0].post_office_city

def saveTweet(tweet, signal, address, lng, lat):  # save a sTweet
    stweet = sTweet.objects.create(text=tweet.text)
    stweet.signal = signal
    stweet.create_at = tweet.created_at
    stweet.address = "Unknown Location"
    if (tweet.coordinates is not None):
        stweet.longitude = tweet.coordinates['coordinates'][0]
        stweet.latitude = tweet.coordinates['coordinates'][1]        
        stweet.address = location(stweet.latitude, stweet.longitude)
    else:
        stweet.longitude = None
        stweet.latitude = None        
    stweet.save()


def Result(request):
    return render(request, "app/result.html", {})

# for AJAX predicting 1 line of tweet's text
def PredictionTweet(request):
    tweetText = request.GET.get('tweet_text')
    result = predict(tweetText)
    return JsonResponse(signals[result], safe=False)


def Predict(request):
    return render(request, "app/predict.html", {})


# for AJAX calling
@csrf_exempt
def LoadTweets(request):
    tweets = sTweet.objects.all()
    result = ""
    for tweet in tweets:
        result += "<tr style='font-family:Verdana; font-size:18px;'><td>" + \
            signals[tweet.signal]+"</td><td>" + tweet.text+"</td><td><img src='/static/image/bullets/" + \
            tweet.signal+".png' height='10' width='10'></td></tr>"
    return JsonResponse(result, safe=False)


def Group(request):
    return render(request, "app/group.html", {})

def Export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename="report.csv"'
    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    tweets = sTweet.objects.all()
    for tweet in tweets:
        print(tweet.text)
        writer.writerow([tweet.tid, tweet.text.encode('utf-8'), tweet.signal,tweet.longitude,tweet.latitude,tweet.address,tweet.create_at])
    return response

    
def ExportGroup(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename="report.csv"'
    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    tweets = sTweet.objects.order_by('signal')
    for tweet in tweets:
        print(tweet.text)
        writer.writerow([tweet.tid, tweet.text.encode('utf-8'), tweet.signal,tweet.longitude,tweet.latitude,tweet.address,tweet.create_at])
    return response

# for AJAX calling
@csrf_exempt
def GroupTweets(request):
    #tweets = sTweet.objects.all()
    tweets = sTweet.objects.order_by('signal')
    result = ""
    for tweet in tweets:
        result += "<tr style='font-family:Verdana; font-size:18px;'><td>" + \
            signals[tweet.signal]+"</td><td>" + tweet.text+"</td><td><img src='/static/image/bullets/" + \
            tweet.signal+".png' height='10' width='10'></td></tr>"
    return JsonResponse(result, safe=False)

def Map(request):
    return render(request, "app/map.html", {})

def MapData(request):
    tweets = sTweet.objects.all()
    #data = serializers.serialize( "python", tweets )
    CategorizeTweets()
    tweet_list = list(tweets.values())
    return JsonResponse(tweet_list, safe=False)

# for pie chart information
def CategorizeTweets():
    tweets = sTweet.objects.all()
    fieldname = 'signal'
    queryset = sTweet.objects.values(fieldname).order_by(
        fieldname).annotate(the_count=Count(fieldname))
    info = [["signal", "count"]]
    for each in queryset:
        row = [signals[each['signal']], each['the_count']]
        info.append(row)
    return info

def ChartView(request):
    data = CategorizeTweets()    
    return render(request, "app/chart.html", {'info': json.dumps(data)})

def Report(request):
    return render(request, "app/report.html", {})

@csrf_exempt
def LoadCity(request):
    postal_code = request.GET['search_keyword']
    zipcode = search.by_zipcode(postal_code)
    #json_str = json.dumps(zipcode.major_city)
    json_str = json.dumps(zipcode.post_office_city)
    resp = json.loads(json_str)
    return JsonResponse(resp, safe=False)


def MapMarker(request):
    return render(request, "app/mapMarker.html", {})





