"""
크론 작업으로 yahoo finance api에서 주식 데이터를 수집하는 스크립트
"""
from datetime import datetime, timezone, timedelta, date
import pandas as pd

import requests
import psycopg2
from psycopg2.extras import execute_values
from common import logger, DB_PARAMS
import pytz


symbols = ["TIP", "QQQ", "GLD", "SPY", "BIL"]

def build_price_dict(data: dict) -> dict:
    """
    Yahoo Finance JSON → {date: close} 딕셔너리 변환
    """
    # api 응답은 json 형식으로 되어있고,
    # 'chart' → 'result' → 'timestamp'와 'close'를 추출하여 딕셔너리로 변환한다.
    result = data['chart']['result'][0]
    timestamps = result['timestamp']
    closes = result['indicators']['quote'][0]['close']

    price_dict = {}
    for ts, close in zip(timestamps, closes):
        if close is not None: # 종가가 None이 아닌 경우에만 저장한다.
            # 타임 스탬프를 UTC 기준 datetime 으로 반환한다. ex) 2024-05-14 07:00:00+00:00 timezone aware
            # date() 메서드를 사용하여 날짜만 추출한다. ex) 2024-05-14
            # 파이썬에서는 datetime객체와 date 객체가 따로 존재한다. 
            dt = datetime.fromtimestamp(ts, tz=timezone.utc).date()
            price_dict[dt] = round(close, 4)
    return price_dict

def apply_fallback(price_dict: dict, symbol: str, start: date, end: date) -> list:
    """
    start ~ end 평일 기준으로 price_dict에서 가격이 없으면 이전 종가로 채움
    처음부터 결측이면 아무것도 못채워주는 한계가 있다.
    """
    # date_range는 날짜의 연속된 리스트를 만드는 pandas 함수이다.
    # freq='B'는 평일만 포함한다.
    # 결과가 datetime 객체로 반환되므로 .date를 사용하여 날짜만 추출한다.
    all_weekdays = pd.date_range(start=start, end=end, freq='B').date
    output = []
    last_price = None

    # 2. 모든 영업일에 대해 반복한다.
    for d in all_weekdays:
        # 해당 날짜에 데이터가 있으면 last_price를 업데이트한다.
        if d in price_dict:
            last_price = price_dict[d]
        # last_price가 있다면(이전에 있었거나, 오늘 데이터가 있는 경우)
        # 튜플을 결과 리스트에 추가한다.
        if last_price is not None:
            output.append((d, symbol, last_price))
    return output


def save_to_db(data):
    """
    주식 데이터를 DB에 저장하는 함수.
    """
    if not data:
        logger.info("저장할 데이터가 없습니다.")
        return

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    logger.info("DB 저장 완료: %d건", len(data))

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            date DATE NOT NULL,
            ticker VARCHAR(10) NOT NULL,
            price NUMERIC(13,4) NOT NULL,
            PRIMARY KEY (date, ticker)
        );
    """)

    try:
        query = """
            INSERT INTO prices (date, ticker, price)
            VALUES %s
            ON CONFLICT (date, ticker) DO NOTHING
        """
        execute_values(cur, query, data)
        conn.commit()
        logger.info("DB 저장 완료: %d건", len(data))
    except Exception: # pylint: disable=broad-except
        logger.error("DB 저장 실패", exc_info=True)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fetch_stock_data(symbol, start_est, end_est, max_fallback_days=3):
    """
    주식 데이터를 수집하여 DB에 저장하는 함수.
    """
    logger.info("작업 시작: %s [%s ~ %s]", symbol, start_est, end_est)

    now_est_timestamp = int(end_est.timestamp())
    start_est_timestamp = int(start_est.timestamp())

    period1, period2 = start_est_timestamp, now_est_timestamp

    response = requests.get(
        f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={
            'period1': period1,
            'period2': period2,
            'interval': '1d'
        },
        headers={'User-Agent': 'Mozilla/5.0'},
        timeout=15
    ).json()

    try:
        start_date = start_est.date()
        end_date = end_est.date()
        price_dict = build_price_dict(response) # json 응답을 딕셔너리로 변환한다.
        filled_data = apply_fallback(price_dict, symbol, start_date, end_date) # 응답으로 결측치를 채운다.
        
        
        save_to_db(filled_data)
        logger.info("작업 완료: %s, 저장된 데이터 %d건", symbol, len(filled_data))
    except Exception as e:
        logger.error("데이터 파싱 실패 [%s]: %s", symbol, e, exc_info=True)




# 전체 데이터 수집
est = pytz.timezone('US/Eastern')

# 현재 시간을 EST로 변환
now_est = datetime.now(est)
start_est = now_est - timedelta(days=100)

# 전체 데이터 수집
for sym in symbols:
    fetch_stock_data(sym, start_est, now_est)
