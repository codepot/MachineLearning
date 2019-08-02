from django.conf.urls import url
from app import views

urlpatterns = [
   
    url(r'^home/$', views.Home.as_view()),  # HOME PAGE IS HERE
    url(r'^search/$', views.Search),

    url(r'^tweets/$', views.Tweets),
    
    url(r'^result/$', views.Result),
    url(r'^load_tweets/$', views.LoadTweets),	# download tweets - ajax

    #display in group
    url(r'^group/$', views.Group),
    url(r'^group_tweets/$', views.GroupTweets),	# download tweets in group- ajax

    url(r'^map/$', views.Map),
    url(r'^mapData/$', views.MapData),

    url(r'^chart/$', views.ChartView),

    url(r'^export/$', views.Export),
    url(r'^export_group/$', views.ExportGroup),


    url(r'^report/$', views.Report), #same as analysi, but using tabs


    url(r'^download_tweets/$', views.DownloadTweets),	# download tweets - ajax

    #predict 1 line of tweet
    url(r'^predict/$', views.Predict),
    url(r'^predict_tweet/$', views.PredictionTweet), #for AJAX call

    
    url(r'^city/$', views.LoadCity), #Ajax return city by zipcode
    url(r'^marker/$', views.MapMarker),    
    
]