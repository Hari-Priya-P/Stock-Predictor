# 12, 26 for short-term; 50, 200 for long-term
def calc_ema(prices):
    sma_list = prices[:5]
    ema_prev = sum(sma_list) / (len(sma_list) * 1.0)
    ema_list = prices[5:]
    n = 6
    for price in ema_list:
        k = 2.0 / (n + 1)
        ema = (price * k) + (ema_prev * (1 - k))
        ema_prev = ema
        n += 1
    return ema_prev


def calc_macd(ema_short, ema_long):
    return ema_short - ema_long


def calc_rsi(prices):
    ups = 0.0
    downs = 0.0
    n = len(prices) - 1
    for i in range(n):
        change = prices[i + 1] - prices[i]
        if change > 0:
            ups += change
        else:
            downs += abs(change)
    avg_ups = ups / (n * 1.0)
    avg_downs = downs / (n * 1.0)
    if avg_downs != 0 or avg_downs != 0.0:
        rs = avg_ups / (avg_downs * 1.0)
    else:
        rs = avg_ups
    rsi = 100 - (100.0 / (1 + rs))
    return rsi


def get_suggestion(macd, rsi):
    if macd > 0:
        if rsi < 70:
            suggestion = 'BUY'
        else:
            suggestion = 'HOLD'
    else:
        if rsi > 30:
            suggestion = 'SELL'
        else:
            suggestion = 'HOLD'
    return suggestion