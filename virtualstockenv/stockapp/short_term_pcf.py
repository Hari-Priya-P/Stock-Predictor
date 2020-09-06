import mysql.connector
import numpy as np
from stockapp.indicator_models import calc_ema, calc_macd, calc_rsi, get_suggestion


def get_short_term(stock, no_of_minutes):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Password1$",
        database='appdata',
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor()
    x_train = []
    t_train = []
    N = 0
    m = 2
    M = m + 1
    lamda = 0.0001
    I = np.identity(M)
    predictions = []
    no_of_minutes=int(no_of_minutes)

    mycursor.execute("SELECT sid from stocks where ticker='" + stock + "';")
    result = mycursor.fetchall()
    sid = result[0][0]

    mycursor.execute("SELECT * from real_time where sid='" + str(sid) + "' order by dat desc, tim desc limit 500;")
    result = mycursor.fetchall()
    result.reverse()
    for row in result:
        x_train.append(N + 1)
        t_train.append(float(row[6]))
        N += 1
    for pred_no in range(no_of_minutes):
        x_new = x_train[len(x_train) - 1] + 1
        X = np.ones((N, M), dtype=float)
        for x in range(len(x_train)):
            for i in range(M):
                X[x][i] = pow(x_train[x], i)
        Y = np.array(t_train).reshape(N, 1)
        xtx = np.dot(X.T, X) + (lamda*I)
        xtx_inv = np.linalg.inv(xtx)
        w = np.dot(np.dot(xtx_inv, X.T), Y)
        x_t = [pow(x_new, i) for i in range(M)]
        x_t = np.array(x_t).reshape(1, M)
        pred_t = (np.dot(x_t, w))[0][0]
        predictions.append(pred_t)
        x_train.remove(x_train[0])
        t_train.remove(t_train[0])
        x_train.append(x_new)
        t_train.append(pred_t)
        for x in range(len(x_train)):
            x_train[x] -= 1
    ema_12 = calc_ema(t_train[-12:])
    ema_26 = calc_ema(t_train[-26:])
    macd = calc_macd(ema_12, ema_26)
    rsi = calc_rsi(t_train[-15:])
    suggestion = get_suggestion(macd, rsi)
    prices, ema_vals, rsi_vals = [], [], []
    for row in result:
        prices.append(float(row[5]))
    for p in predictions:
        prices.append(float(p))
    i = 10
    while i < len(prices):
        sample = prices[:i]
        ema_vals.append(calc_ema(sample))
        rsi_vals.append(calc_rsi(sample))
        i += 1
    size = len(ema_vals)
    price = prices[-size:]
    return predictions, suggestion, price, ema_vals, rsi_vals
