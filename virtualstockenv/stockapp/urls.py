from . import views
from django.urls import path, include

from django.contrib.auth.models import User
from stockapp.models import Historical, Stocks, RealTime
from rest_framework import routers

from stockapp.views import UserViewSet, HistoricalViewSet, TickerViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'api/users', UserViewSet)

router.register(r'api/Ticker', TickerViewSet)

router.register(r'api/History', HistoricalViewSet)

#router.register(r'api/Realtime', RealTimeViewSet)



urlpatterns = [

    path('', views.myhome, name='My-Home'),
    path('about/', views.about, name='page-about'),
    path('Contact/', views.contact, name='contact'),
    path('learning_page/', views.learning_page, name='learning_page'),
    path('predict/', views.predict, name='PREDICT'),
    path('longpredict/', views.longpredict, name='LONG-PREDICT'),
    path('shortpredict/', views.shortpredict, name='SHORT-PREDICT'),
    path('compare/', views.compare, name='compare'),
    path('threshold/', views.threshold, name='threshold'),
    path('analysis/', views.analysis, name='analysis'),
    path('long_analysis/', views.long_analysis, name='long_analysis'),
    path('short_analysis/', views.short_analysis, name='short_analysis'),
    path('AAPL/', views.aapl_profile, name='aapl_profile'),
    path('AMZN/', views.amzn_profile, name='amzn_profile'),
    path('FB/', views.fb_profile, name='fb_profile'),
    path('GOOGL/', views.googl_profile, name='googl_profile'),
    path('NFLX/', views.nflx_profile, name='nflx_profile'),
    path('TRIP/', views.trip_profile, name='trip_profile'),
    path('TSLA/', views.tsla_profile, name='tsla_profile'),
    path('TWTR/', views.twtr_profile, name='twtr_profile'),
    path('VAC/', views.vac_profile, name='vac_profile'),
    path('YELP/', views.yelp_profile, name='yelp_profile'),

]