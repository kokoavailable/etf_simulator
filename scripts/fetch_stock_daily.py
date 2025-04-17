"""
크론 작업으로 yahoo finance api에서 주식 데이터를 수집하는 스크립트
"""
from datetime import datetime, timezone, timedelta, date
import pandas as pd

import requests
import psycopg2
from psycopg2.extras import execute_batch
from common import logger, DB_PARAMS
import pytz


symbols = ["TIP", "QQQ", "GLD", "SPY", "BIL"]

def get_yahoo_timestamp_range(start_date: datetime, end_date: datetime) -> tuple[int, int]:
    """
    Yahoo Finance API에 사용할 정확한 시작/종료 타임스탬프 생성 함수.
    - 시작일: 해당일 05:00 UTC
    - 종료일: 해당일 05:00 UTC + 1일 (즉, 다음날 05:00)
    """
    period1 = start_date.replace(hour=5, minute=0, second=0, microsecond=0)
    period2 = end_date.replace(hour=5, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return int(period1.timestamp()), int(period2.timestamp())

def build_price_dict(symbol: str, data: dict) -> dict:
    """
    Yahoo Finance JSON → {date: close} 딕셔너리 변환
    """
    result = data['chart']['result'][0]
    timestamps = result['timestamp']
    closes = result['indicators']['quote'][0]['close']

    price_dict = {}
    for ts, close in zip(timestamps, closes):
        if close is not None:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc).date()
            price_dict[dt] = round(close, 4)
    return price_dict

def apply_fallback(price_dict: dict, symbol: str, start: date, end: date) -> list:
    """
    start ~ end 평일 기준으로 price_dict에서 가격이 없으면 이전 종가로 채움
    """
    all_weekdays = pd.date_range(start=start, end=end, freq='B').date
    output = []
    last_price = None

    for d in all_weekdays:
        if d in price_dict:
            last_price = price_dict[d]
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

    try:
        query = """
            INSERT INTO prices (date, ticker, price)
            VALUES (%s, %s, %s)
            ON CONFLICT (date, ticker) DO NOTHING
        """
        execute_batch(cur, query, data)
        conn.commit()
        logger.info("DB 저장 완료: %d건", len(data))
    except Exception: # pylint: disable=broad-except
        logger.error("DB 저장 실패", exc_info=True)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fetch_stock_data(symbol, start_date, end_date, max_fallback_days=3):
    """
    주식 데이터를 수집하여 DB에 저장하는 함수.
    """
    logger.info("작업 시작: %s [%s ~ %s]", symbol, start_date, end_date)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    period1, period2 = get_yahoo_timestamp_range(start_dt, end_dt)

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
        price_dict = build_price_dict(symbol, response)
        filled_data = apply_fallback(price_dict, symbol, start_dt.date(), end_dt.date())
        save_to_db(filled_data)
        logger.info("작업 완료: %s, 저장된 데이터 %d건", symbol, len(filled_data))
    except Exception as e:
        logger.error("데이터 파싱 실패 [%s]: %s", symbol, e, exc_info=True)




# 전체 데이터 수집
est = pytz.timezone('US/Eastern')

# 현재 시간을 EST로 변환
now_est = datetime.now(est)

# YYYY-MM-DD 형식으로 날짜 문자열 생성
end_date_str = now_est.strftime("%Y-%m-%d")
start_date_str = (now_est - timedelta(days=100)).strftime("%Y-%m-%d")

# 전체 데이터 수집
for sym in symbols:
    fetch_stock_data(sym, start_date_str, end_date_str)
