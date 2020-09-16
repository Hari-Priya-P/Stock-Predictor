import mysql.connector
from datetime import date
import datetime
import time
import yahoo_fin.stock_info as yf


# list of 10 stocks
stocks = ['AAPL', 'AMZN', 'FB', 'GOOGL', 'NFLX', 'TSLA', 'TWTR', 'YELP', 'VAC', 'TRIP']

# connect to mysql database
mydb = mysql.connector.connect(
    host="localhost",
    user="<user>",
    passwd="<password>",
    database="appdata",
    auth_plugin='mysql_native_password',
)

mycursor = mydb.cursor()
mycursor.execute("SET SQL_SAFE_UPDATES = 0;")


# get historical stock data
def get_hist():

    for stock in stocks:
        mycursor.execute("SELECT sid from stocks where ticker='" + stock + "'")
        result = mycursor.fetchall()
        sid = result[0][0]

        data = yf.get_data(ticker=stock, start_date=date.today())
        dat = date.today()
        open_value = data.iloc[0, :]['open']
        close_value = data.iloc[0, :]['close']
        low = data.iloc[0, :]['low']
        high = data.iloc[0, :]['high']
        volume = data.iloc[0, :]['volume']
        sql = "INSERT IGNORE INTO historical (sid,dat,open_value,low,high,close_value,volume) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s)"
        val = (str(sid), str(dat), str(open_value), str(low), str(high), str(close_value), str(volume))
        mycursor.execute(sql, val)
        mydb.commit()


def get_real():
    limit = 2500
    now = time.time()
    ts = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
    dt_array = ts.strip().split(" ")
    dat = dt_array[0].strip()
    tim = dt_array[1].strip()

    for stock in stocks:
        details = yf.get_quote_table(stock)

        open_value = str(details['Open']).replace(',', '')
        day_range = str(details['Day\'s Range']).strip().split("-")
        low = day_range[0].strip().replace(',', '')
        high = day_range[len(day_range) - 1].strip().replace(',', '')
        close_value = str(yf.get_live_price(stock))
        volume = str(details['Volume']).replace(',', '')

        mycursor.execute("SELECT sid from stocks where ticker='" + stock + "'")
        result = mycursor.fetchall()
        sid = str(result[0][0])

        sql = "INSERT IGNORE INTO real_time (sid,dat,tim,open_value,low,high,close_value,volume) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (sid, dat, tim, open_value, low, high, close_value, volume)
        mycursor.execute(sql, val)
        mydb.commit()


        mycursor.execute("SELECT count(*) from real_time where sid='" + str(sid) + "'")
        result = mycursor.fetchall()
        rows = int(result[0][0])
        if rows > limit:
            num_delete = rows - limit
            sql = "delete from real_time where sid='" + str(sid) + "' order by dat asc, tim asc limit " \
                  + str(num_delete) + ";"
            mycursor.execute(sql)
            mydb.commit()

