import time
import pyupbit
import datetime
import requests
import threading

access = "Tmgxa6qGebzmVlozAR8G3nMboeuxxxiOkXewnXQM"
secret = "eUdhpZrtbPSzx6dQiuc0U6ZBA3LdoKQJUGZ7aoox"
myToken = "xoxb-1998829143459-2045555121459-y9mKlKgku5WmWR1DHckWybtv"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("자동매매 시작합니다.")
# 시작 메세지 슬랙 전송
post_message(myToken,"#yungjun", "자동매매 시작합니다.")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETC") #9:00
        end_time = start_time + datetime.timedelta(days=1) #9:00 + 1일
        # 9:00 < 현재 < #8:59:50
        if timer == 1:
            post_message(myToken,"#yungjun", "Today target_price =" + str(target_price))
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-ETC", 0.1)  # k값 변화에 따라
            current_price = get_current_price("KRW-ETC")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-ETC", krw*0.9995)
                    post_message(myToken,"#yungjun", "ETC 매수 결과 : " + str(buy_result))
        else:
            btc = get_balance("ETC")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-ETC", btc*0.9995)
                post_message(myToken,"#yungjun", "ETC 매도 결과 : " + str(sell_result))
                timer = 1
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#yungjun", e)
        time.sleep(1) 