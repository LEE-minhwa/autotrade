import time
import pyupbit
import datetime
import requests

access = "H6jq1r1cKUYzgm6hNeVLXw9aVkvVPKwzECNUANc8"
secret = "xJJ12UPXKFlxILPPM5FqnmVVbkm5FcJZqNa2S8b8"
myToken = ""

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
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#crypto", "ETH start")
timer = 7500


# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-ETH") #9:00
        end_time = start_time + datetime.timedelta(days=1) #9:00 + 1일
        # 9:00 < 현재 < #8:59:50
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-ETH", 0.3)  # k값 변화에 따라
            current_price = get_current_price("KRW-ETH")
            if timer > 7200:
                post_message(myToken,"#crypto", "오늘의 목표가 : "+ str(target_price))
                post_message(myToken,"#crypto", "오늘의 매수가 : "+ str(target_price*0.98))
                timer = 0
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    #buy_result = upbit.buy_market_order("KRW-ETH", krw*0.9995)
                    buy_result = upbit.buy_limit_order("KRW-BTC", int(target_price*0.98), float(krw/(target_price*0.982)))
                    post_message(myToken,"#crypto", "ETH buy : " + str(buy_result))
        else:
            btc = get_balance("ETH")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-ETH", btc*0.9995)
                post_message(myToken,"#crypto", "ETH buy : " + str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#crypto", e)
        time.sleep(1) 