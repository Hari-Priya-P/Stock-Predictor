from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from rest_framework import routers, serializers, viewsets
from virtualstockenv.serializers import UserSerializer, HistoricalSerializer, TickerSerializer, RealTimeSerializer, ThresholdsSerializer
from django.contrib.auth.models import User
from stockapp.models import Historical, Stocks, RealTime, Thresholds
from datetime import date, datetime, timedelta
from stockapp.short_term_pcf import get_short_term
from stockapp.long_term_nn import get_long_term
from stockapp.queries import run_queries
import json
import time
from django.db.models import Avg
# Create your views here.


def myhome(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    stocks = Stocks.objects.values('sid', 'ticker')
    stock_data = dict()
    for stock in stocks:
        sid = str(stock['sid'])
        ticker = str(stock['ticker'])
        record = RealTime.objects.values('close_value').filter(sid=sid).order_by('-dat', '-tim')[:1]
        price = str(record[0]['close_value'])
        stock_data[ticker] = price

    stock_tickers = list()
    prices = list()

    for stock, price in stock_data.items():
        stock_tickers.append(stock)
        prices.append(float(price))

    price_series = {
        'name': 'Stock Prices',
        'data': prices
    }

    chart = {
        'chart': {'type': 'bar'},
        'plotOptions': {
            'series': {
                'colorByPoint': 'true',
            }
        },
        'title': {'text': 'Overview of Latest Stock Prices for all Stocks'},
        'xAxis': {'title': {'text': 'Stock Tickers'}, 'categories' : stock_tickers},
        'yAxis': {'title': {'text': 'Price'}},
        'series': [price_series]
    }

    dump = json.dumps(chart)

    username = request.user.username

    return render(request, 'stockapp/myhome.html', {'myhome_page': 'active', 'price': stock_data, 'chart': dump, 'username': username})


def about(request):
	stocks = Stocks.objects.values('ticker')
	return render(request, 'stockapp/about.html', {'stocks': stocks})


def contact(request):
    return render(request, 'stockapp/contact.html')

# remove
def home(request):
    return render(request, 'stockapp/default.html')


def landing(request):
    return render(request, 'stockapp/landing_page.html')

def learning_page(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/learning_page.html', {'learning_page': 'active'})

def predict(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/predict.html', {'predict_page': 'active'})

def analysis(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/analysis.html', {'analysis_page': 'active'})


def long_analysis(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    if request.method == 'POST':
        if request.POST.get('date-start') and request.POST.get('date-end') and request.POST.get('stock') and request.POST.get('metric') and request.POST.get('frequency'):
            start_date = request.POST.get('date-start')
            end_date = request.POST.get('date-end')
            stock = request.POST.get('stock')
            value = request.POST.get('metric')
            frequency = request.POST.get('frequency')
    else:
        start_date = '2020-01-01'
        end_date = datetime.today().strftime('%Y-%m-%d')
        stock = 'AAPL'
        value = 'close_value'
        frequency = 'daily'

    sid = Stocks.objects.filter(ticker=stock).values('sid')
    stock_id = sid[0]['sid']
    if frequency == 'daily':
        dataset = Historical.objects.values('dat', value).filter(sid=stock_id).filter(dat__range=(start_date, end_date))
    elif frequency == 'monthly':
        dataset = Historical.objects.filter(dat__range=(start_date, end_date)).values('dat__year','dat__month').annotate(avg=Avg('close_value'))
    else:
        dataset = Historical.objects.filter(dat__range=(start_date, end_date)).values('dat__year','dat__week').annotate(avg=Avg('close_value'))
    dates = list()
    price = list()

    if frequency == 'daily':
        for entry in dataset:
            dates.append(str(entry['dat']))
            price.append(entry[value])
    else:
        for entry in dataset:
            year = str(entry['dat__year'])
            if frequency == 'monthly':
                freq = str(entry['dat__month'])
            else:
                freq = str(entry['dat__week'])
            dates.append(year+"-"+freq)
            price.append(entry['avg'])


    price_series = {
        'name': value,
        'data': price,
    }

    x_title = 'Dates (YY-MM-DD)'
    if frequency == 'monthly':
        x_title = 'Months (YY-MM)'
    elif frequency == 'weekly':
        x_title = 'Weeks (YY-Week)'


    if value == "volume":
        y_units = " (shares)"
    else:
        y_units = " (USD)"

    chart = {
        'chart': {'type': 'areaspline'},
        'title': {'text': stock+' Stock Analysis from '+start_date+' to '+end_date},
        'xAxis': {'title': {'text': x_title}, 'categories' : dates},
        'yAxis': {'title': {'text': value+y_units}},
        'series': [price_series]
    }

    dump = json.dumps(chart)
    historical = Historical.objects.filter(sid=stock_id).filter(dat__range=(start_date, end_date)).order_by('-dat')

    if start_date >= end_date:
        return render(request, 'stockapp/historical_data.html', {'chart': dump, 'historical': historical, 'msg': 'Please enter valid dates!'})
    return render(request, 'stockapp/historical_data.html', {'chart': dump, 'historical': historical})


def long_analysis_new(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    if request.method == 'POST':
        if request.POST.get('date-start') and request.POST.get('date-end') and request.POST.get('stock') and request.POST.get('metric'):
            start_date = request.POST.get('date-start')
            end_date = request.POST.get('date-end')
            stock = request.POST.get('stock')
            value = request.POST.get('metric')
    else:
        start_date = '2020-01-01'
        end_date = datetime.today().strftime('%Y-%m-%d')
        stock = 'AAPL'
        value = 'close_value'

    sid = Stocks.objects.filter(ticker=stock).values('sid')
    stock_id = sid[0]['sid']
    dataset = Historical.objects.values('dat', value).filter(sid=stock_id).filter(dat__range=(start_date, end_date))
    sample = Historical.objects.values('dat__month').annotate(count=Avg('close_value'))
    print(sample)
    dates = list()
    price = list()

    for entry in dataset:
        dates.append(str(entry['dat']))
        price.append(entry[value])


    price_series = {
        'name': value,
        'data': price,
    }

    if value == "volume":
        y_units = " (shares)"
    else:
        y_units = " (USD)"

    chart = {
        'chart': {'type': 'areaspline'},
        'title': {'text': stock+' Stock Analysis from '+start_date+' to '+end_date},
        'xAxis': {'title': {'text': 'Dates (YY-MM-DD)'}, 'categories' : dates},
        'yAxis': {'title': {'text': value+y_units}},
        'series': [price_series]
    }

    dump = json.dumps(chart)
    historical = Historical.objects.filter(sid=stock_id).filter(dat__range=(start_date, end_date)).order_by('-dat')


    return render(request, 'stockapp/historical_data.html', {'chart': dump, 'historical': historical})


def short_analysis(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    if request.method == 'POST':
        if request.POST.get('start-time') and request.POST.get('end-time') and request.POST.get('stock'):
            start_time = request.POST.get('start-time')
            end_time = request.POST.get('end-time')
            stock = request.POST.get('stock')


            today = datetime.today().strftime('%Y-%m-%d')
            sid = Stocks.objects.filter(ticker=stock).values('sid')

            stock_id = sid[0]['sid']
            dataset = RealTime.objects.values('tim', 'close_value').filter(sid=stock_id).filter(dat=today).filter(tim__range=(start_time, end_time))

            real_time = run_queries(str(stock))
                
            if not dataset:
                return render(request, 'stockapp/query.html', {'real_time': real_time})

            
            times = list()
            price = list()

            for entry in dataset:
                times.append(str(entry['tim']))
                price.append(entry['close_value'])


            price_series = {
                'name': 'Stock Price',
                'data': price,
            }

            chart = {
                'chart': {'type': 'line'},
                'title': {'text': 'Stock Price Analysis from '+start_time+' to '+end_time},
                'xAxis': {'title': {'text': 'Time (HH:MM:SS)'}, 'categories' : times},
                'yAxis': {'title': {'text': 'Price (USD)'}},
                'series': [price_series]
            }

            dump = json.dumps(chart)

            return render(request, 'stockapp/query.html', {'chart': dump, 'real_time': real_time})
    else:
        stock = 'AAPL'
        sid = Stocks.objects.filter(ticker=stock).values('sid')
        stock_id = sid[0]['sid']
        real_time = run_queries(str(stock))
        today = datetime.today().strftime('%Y-%m-%d')
        dataset = RealTime.objects.values('dat', 'tim', 'close_value').filter(sid=stock_id).order_by('-dat', '-tim')[:500]
        times = list()
        price = list()

        for entry in dataset:
            times.append(str(entry['tim']))
            price.append(entry['close_value'])

        times.reverse()
        price.reverse()


        price_series = {
            'name': 'Stock Price',
            'data': price,
        }

        chart = {
            'chart': {'type': 'line'},
            'title': {'text': stock + ' Stock Price Analysis'},
            'xAxis': {'title': {'text': 'Time (HH:MM:SS)'}, 'categories' : times},
            'yAxis': {'title': {'text': 'Price (USD)'}},
            'series': [price_series]
        }
        dump = json.dumps(chart)
        return render(request, 'stockapp/query.html', {'chart': dump, 'real_time': real_time})


def threshold(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    stocks = Stocks.objects.values('sid', 'ticker')
    stock_data = dict()
    for stock in stocks:
        sid = str(stock['sid'])
        ticker = str(stock['ticker'])
        record = RealTime.objects.values('close_value').filter(sid=sid).order_by('-dat', '-tim')[:1]
        price = str(record[0]['close_value'])
        stock_data[ticker] = price
    if request.method == 'POST':
        if request.POST.get('stock') and request.POST.get('threshold'):
            name=request.POST.get('stock')
            id=Stocks.objects.get(ticker=name)
            price = RealTime.objects.filter(sid=id.sid).latest('dat', 'tim')

            threshold = Thresholds()
            threshold.ticker=name
            threshold.price=price.close_value
            threshold.threshold = request.POST.get('threshold')
            threshold.username = request.user.username
            threshold.satisfied = 0

            threshold.save()

    context = {

        'threshold': Thresholds.objects.filter(username=request.user.username).filter(satisfied=0).values('ticker', 'threshold', 'price'),
        'stock_data': stock_data,
        'threshold_page': 'active'

    }
    return render(request, 'stockapp/threshold.html', context)


def longpredict(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    preds_input = "Please enter the number of days you would like the predictions for (max 100):"
    if request.method == 'POST':
        name = request.POST.get('stock')
        no_of_days = request.POST.get('quantity')
        name = str(name)     
        num=int(no_of_days)
        if num > 100:
        	return render(request, 'stockapp/predict_form.html', {'preds_input': preds_input, 'title': 'Long Term Prediction', 'alert': 'Invalid Value! Please enter a value less than 100.'})
        predicted, suggestion, price, ema, rsi = get_long_term(name, no_of_days)
        prediction_results = dict()
        for i in range(num):
            prediction_results["Day " + str(i+1)] = str(predicted[i])

        prediction_msg = "Predictions for stock " + str(name) + " for the next " + str(no_of_days) + " day(s) are:"
        if suggestion == "BUY":
            suggestion_msg = "As we observe an upcoming uptrend based on the predictions, we suggest you to " + str(suggestion) + " " + str(name) + " stocks."
        elif suggestion == "SELL":
            suggestion_msg = "As we observe an upcoming downtrend based on the predictions, we suggest you to " + str(suggestion) + " " + str(name) + " stocks."
        else:
        	suggestion_msg = "As we observe an unstable market based on the predictions, we suggest you to " + str(suggestion) + " " + str(name) + " stocks."

        chart = {
            'chart': {'type': 'line'},
            'title': {'text': 'Price, EMA and RSI Plot for '+str(name)+' since past 1 year including the above predictions'},
            'xAxis': {'title': {'text': 'Points of Time'}},
            'yAxis': {'title': {'text': 'Values'}},
            'series': [{
            'name': 'Price',
            'data': price,
            'color': 'green'
            },

            {
            'name': 'EMA',
            'data': ema,
            'color': 'blue'
            },

            {
            'name': 'RSI',
            'data': rsi,
            'color': 'red'
            }]
            }

        dump = json.dumps(chart)
        

        return render(request, 'stockapp/predict_form.html', {'preds_input': preds_input, 'predictions': prediction_results, 'suggestion': suggestion_msg, 'prediction_msg': prediction_msg, 'chart': dump})
    else:
        return render(request, 'stockapp/predict_form.html', {'preds_input': preds_input, 'title': 'Long Term Prediction'})


def shortpredict(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    preds_input = "Please enter the number of minutes you would like the predictions for (max 500):"
    if request.method == 'POST':
        name = request.POST.get('stock')
        no_of_mins = request.POST.get('quantity')
        name = str(name)     
        num=int(no_of_mins)
        if num > 500:
        	return render(request, 'stockapp/predict_form.html', {'preds_input': preds_input, 'title': 'Short Term Prediction', 'alert': 'Invalid Value! Please enter a value less than 500.'})
        predicted, suggestion, price, ema, rsi = get_short_term(name, no_of_mins)
        prediction_results = dict()
        for i in range(num):
            prediction_results["Minute " + str(i+1)] = str(predicted[i])

        prediction_msg = "Predictions for stock " + str(name) + " for the next " + str(no_of_mins) + " minute(s) are:"
        if suggestion == "BUY":
            suggestion_msg = "As we observe an upcoming uptrend based on the predictions, we suggest you to " + str(suggestion) + " " + str(name) + " stocks."
        elif suggestion == "SELL":
            suggestion_msg = "As we observe an upcoming downtrend based on the predictions, we suggest you to " + str(suggestion) + " " + str(name) + " stocks."
        else:
        	suggestion_msg = "As we observe an unstable market based on the predictions, we suggest you to " + str(suggestion) + " " + str(name) + " stocks."

        chart = {
            'chart': {'type': 'line'},
            'title': {'text': 'Price, EMA and RSI Plot for '+str(name)+' since past 1 day including the above predictions'},
            'xAxis': {'title': {'text': 'Points of Time'}},
            'yAxis': {'title': {'text': 'Values'}},
            'series': [{
            'name': 'Price',
            'data': price,
            'color': 'green'
            },

            {
            'name': 'EMA',
            'data': ema,
            'color': 'blue'
            },

            {
            'name': 'RSI',
            'data': rsi,
            'color': 'red'
            }]
            }

        dump = json.dumps(chart)


        return render(request, 'stockapp/predict_form.html', {'preds_input': preds_input, 'title': 'Short Term Prediction', 'predictions': prediction_results, 'suggestion': suggestion_msg, 'prediction_msg': prediction_msg, 'chart': dump})
    else:
        return render(request, 'stockapp/predict_form.html', {'preds_input': preds_input, 'title': 'Short Term Prediction'})

def aapl_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/aapl.html')

def amzn_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/amzn.html')

def fb_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/fb.html')

def googl_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/googl.html')

def nflx_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/nflx.html')

def trip_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/trip.html')
 
def tsla_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/tsla.html')

def twtr_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/twtr.html')

def vac_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/vac.html')

def yelp_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    return render(request, 'stockapp/yelp.html')

def compare(request):
    if not request.user.is_authenticated:
        return render(request, 'stockapp/landing_page.html')
    if request.method == 'POST':
        stocks = request.POST.getlist('stocks')
        term = request.POST.get('term')
    else:
        stocks = ['FB','TRIP']
        term = 'long'
    no_of_stocks = len(stocks)
    series1 = []
    series2 = []
    avg_vals = dict()
    for i in range(no_of_stocks):
        stock_record = Stocks.objects.values('sid').filter(ticker=stocks[i])
        sid = stock_record[0]['sid']
        if term == 'long':
            record = Historical.objects.values('dat','open_value','low','high','close_value','volume').filter(sid=sid).order_by('-dat')[:270]
        else:
            record = RealTime.objects.values('dat','tim','open_value','low','high','close_value','volume').filter(sid=sid).order_by('-dat','-tim')[:500]
        p, v, d = [], [], []
        o, l, h = [], [], []
        for data in record:
            o.append(data['open_value'])
            l.append(data['low'])
            h.append(data['high'])
            p.append(data['close_value'])
            if term == 'long':
                d.append(str(data['dat']))
            else:
                dt = str(data['dat']) + "," + str(data['tim'])
                d.append(dt)
            v.append(data['volume'])

        d.reverse()
        p.reverse()
        v.reverse()
        prices, volumes = dict(), dict()
        prices['name'] = stocks[i]
        prices['data'] = p
        volumes['name'] = stocks[i]
        volumes['data'] = v
        avgp = sum(p) / (len(p) * 1.0)
        avgv = sum(v) / (len(v) * 1.0)
        avgo = sum(o) / (len(o) * 1.0)
        avgl = sum(l) / (len(l) * 1.0)
        avgh = sum(h) / (len(h) * 1.0)
        avg_vals[stocks[i]] = [avgo, avgl, avgh, avgp, avgv]
        series1.append(prices)
        series2.append(volumes)
        if term == 'long':
            period = '1 year'
        else:
            period = '1 day'

    chart1 = {
        'chart': {'type': 'line'},
        'title': {'text': 'Comparison of Stock Performance over the past ' + period},
        'xAxis': {'title': {'text': 'Points of Time'}},
        'yAxis': {'title': {'text': 'Price (USD)'}},
        'series': series1
        }

    dump1 = json.dumps(chart1)

    chart2 = {
        'chart': {'type': 'line'},
        'title': {'text': 'Comparison of Stock Volumes traded over the past ' + period},
        'xAxis': {'title': {'text': 'Points of Time'}},
        'yAxis': {'title': {'text': 'Volume (Shares)'}},
        'series': series2
        }

    dump2 = json.dumps(chart2)

    return render(request, 'stockapp/compare.html', {'chart1': dump1, 'chart2': dump2, 'averages': avg_vals, 'compare_page': 'active'})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ViewSets define the view behavior.
class HistoricalViewSet(viewsets.ModelViewSet):
    queryset = Historical.objects.all()
    serializer_class = HistoricalSerializer


# ViewSets define the view behavior.
class TickerViewSet(viewsets.ModelViewSet):
    queryset = Stocks.objects.all()
    serializer_class = TickerSerializer