import mysql.connector
import datetime


def run_queries(stock):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Password1$",
        database='appdata',
        auth_plugin='mysql_native_password'
    )
    stocks = [
        ('AAPL', 'Apple Inc.'), ('AMZN', 'Amazon.com, Inc.'), ('FB', 'Facebook, Inc.'), ('GOOGL', 'Alphabet Inc.'),
        ('NFLX', 'Netflix, Inc.'), ('TRIP', 'TripAdvisor, Inc.'), ('TSLA', 'Tesla, Inc.'), ('TWTR', 'Twitter, Inc.'),
        ('VAC', 'Marriott Vacations Worldwide Corporation'), ('YELP', 'Yelp Inc.')
    ]
    query_results = dict()
    current_date = datetime.date.today()
    prev_10days = str(datetime.date.today() - datetime.timedelta(days=10))
    # working days in a year = 261 approx
    prev_1year = str(datetime.date.today() - datetime.timedelta(days=270))
    mycursor = mydb.cursor()
    mycursor.execute("SELECT sid from stocks where ticker='" + stock + "';")
    result = mycursor.fetchall()
    sid = result[0][0]
    # 10 days
    mycursor.execute("SELECT min(low), max(high) from historical where sid='" + str(sid) +
                     "' and dat > '" + prev_10days + "';")
    result_10days = mycursor.fetchall()
    min_10days = float(result_10days[0][0])
    max_10days = float(result_10days[0][1])

    mycursor.execute("SELECT min(low), max(high), avg(close_value) from historical where sid='" + str(sid) +
                     "' and dat > '" + prev_1year + "';")
    result_1year = mycursor.fetchall()
    min_1year = float(result_1year[0][0])
    max_1year = float(result_1year[0][1])
    avg_1year = float(result_1year[0][2])

    mycursor.execute("SELECT dat, close_value from historical where sid='" + str(sid) +
                     "' order by dat desc limit 2;")
    result_2days = mycursor.fetchall()
    date = result_2days[0][0]
    prev_close = float(result_2days[0][1])
    if date == current_date:
        prev_close = float(result_2days[1][1])

    mycursor.execute("SELECT low, high, close_value from real_time where sid='" + str(sid) +
                     "' order by dat desc, tim desc limit 1;")
    result_today = mycursor.fetchall()
    min_today = float(result_today[0][0])
    max_today = float(result_today[0][1])
    current_today = float(result_today[0][2])
    change = ((current_today - prev_close) * 100) / prev_close

    if min_today < min_10days:
        min_10days = min_today
    if min_today < min_1year:
        min_1year = min_today
    if max_today > max_10days:
        max_10days = max_today
    if max_today > max_1year:
        max_1year = max_today
    query_results['current_price'] = current_today
    query_results['change'] = round(change, 3)
    query_results['prev_close'] = prev_close
    query_results['min_10days'] = min_10days
    query_results['max_10days'] = max_10days
    query_results['min_1year'] = min_1year
    query_results['max_1year'] = max_1year
    query_results['avg_1year'] = round(avg_1year, 2)

    companies = []
    for ticker, company in stocks:
        if ticker != stock:
            mycursor.execute("SELECT sid from stocks where ticker='" + str(ticker) + "';")
            result = mycursor.fetchall()
            stock_sid = result[0][0]
            mycursor.execute("SELECT avg(close_value) from historical where sid='" + str(stock_sid) +
                             "' and dat > '" + prev_1year + "';")
            stock_result_1year = mycursor.fetchall()
            stock_avg = float(stock_result_1year[0][0])
            if stock_avg < avg_1year:
                companies.append((ticker, company))
        else:
            query_results['company_name'] = company
    query_results['companies'] = companies
    return query_results

