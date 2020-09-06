import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
import mysql.connector
from stockapp.indicator_models import calc_ema, calc_macd, calc_rsi, get_suggestion


def get_long_term(stock, no_of_days):
    mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Password1$",
            database="appdata",
            auth_plugin='mysql_native_password'
        )
    print("Stock: ", stock)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * from stocks where ticker='" + str(stock) + "';")
    result = mycursor.fetchall()
    print("Result: ", result)
    sid = result[0][0]
    mycursor.execute("SELECT * from historical where sid='" + str(sid) + "' order by dat desc limit 240;")
    result = mycursor.fetchall()
    result.reverse()
    window = 5
    data = []
    target = []
    new_input = []
    for i in range(len(result) - window):
        j = i
        input_batch = []
        while j < i + window:
            input_batch.append(float(result[j][5]))
            j += 1
        data.append(input_batch)
        target.append(float(result[j][5]))

    latest = result[-window:]
    for row in latest:
        new_input.append(float(row[5]))
    x = pd.DataFrame(data)
    y = pd.DataFrame(target)
    y = np.reshape(y, (-1, 1))

    scaler_x = MinMaxScaler()
    scaler_y = MinMaxScaler()
    scaler_x.fit(x)
    xscale = scaler_x.transform(x)
    scaler_y.fit(y)
    yscale = scaler_y.transform(y)
    x_train, x_test, y_train, y_test = train_test_split(xscale, yscale)
    model = Sequential()
    model.add(Dense(10, input_dim=window, kernel_initializer='normal', activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(no_of_days, activation='linear'))
    model.compile(loss='mse', optimizer='adam', metrics=['mse', 'mae'])
    history = model.fit(x_train, y_train, epochs=50, batch_size=50, verbose=0, validation_split=0.2)
    xnew = np.array([new_input])
    xnew = scaler_x.transform(xnew)
    ynew = model.predict(xnew)
    ynew = scaler_y.inverse_transform(ynew)
    predictions = []
    for y in ynew[0]:
        predictions.append(y)
    for prediction in predictions:
        target.append(prediction)
    ema_50 = calc_ema(target[-50:])
    ema_200 = calc_ema(target[-200:])
    macd = calc_macd(ema_50, ema_200)
    rsi = calc_rsi(target[-71:])
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

