import time
import pyupbit
import datetime
import requests
import threading

access = "kHbmNmx97Jfo5h96r1ltRusnw6iBcsqhCdRK0YRH"
secret = "cmHxkEw2nYlCUzv6cMQIKgcUxovxoNJylAxHkkPi"
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
print("자동매매 시작합니다.")
# 시작 메세지 슬랙 전송
post_message(myToken,"#sangwoo", "자동매매 시작합니다.")
timer = 0
count = 1

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-QTUM") #9:00
        end_time = start_time + datetime.timedelta(days=1) #9:00 + 1일
        # 9:00 < 현재 < #8:59:50
        timer += 1
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-QTUM", 0.2)  # k값 변화에 따라
            current_price = get_current_price("KRW-QTUM")
            if timer > 10:
                post_message(myToken,"#sangwoo", "오늘의 타겟가 : "+ str(target_price))
                post_message(myToken,"#sangwoo", "오늘의 매수주문가 : "+ str(int(target_price*0.96)))
                timer = 0
            if target_price < current_price < target_price*1.1:
                krw = get_balance("KRW")
                if krw > 5000:
                    #buy_result = upbit.buy_market_order("KRW-DOGE", krw*0.9995)
                    if count == 1:
                        deposit_buy = krw
                        count = 0
                    buy_result = upbit.buy_limit_order("KRW-QTUM", int(target_price*0.96), krw/(int(target_price*0.962)))
                    post_message(myToken,"#sangwoo", "QTUM 매수결과 : " + str(buy_result))
        else:
            btc = get_balance("QTUM")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-QTUM", btc*0.9995)
                deposit_sell = get_balance("KRW")
                post_message(myToken,"#sangwoo", "QTUM 매도결과 : " + str(sell_result))
                post_message(myToken,"#sangwoo", "일일 수익금 : " + deposit_sell-deposit_buy)
                post_message(myToken,"#sangwoo", "일일 수익율 : " + (deposit_sell-deposit_buy)/deposit_buy)
                count = 1
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#sangwoo", e)
        time.sleep(1)