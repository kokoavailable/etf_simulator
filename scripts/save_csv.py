"""
데이터 시트를 받아서 PostgreSQL에 저장하는 스크립트
"""


import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from common import DB_PARAMS

# 2. CSV 파일 로드
CSV_FILE = "price_data.csv"
df = pd.read_csv(CSV_FILE)

# 3. 데이터 변환 (Wide → Long Format)
df_long = df.melt(id_vars=["date"], var_name="ticker", value_name="price")

# 4. 데이터 타입 변환
df_long["date"] = pd.to_datetime(df_long["date"])  # 날짜 변환

# 5. PostgreSQL 연결 및 데이터 삽입
try:
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    # 5-1. 테이블이 존재하지 않으면 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            date DATE NOT NULL,
            ticker VARCHAR(10) NOT NULL,
            price NUMERIC(13,4) NOT NULL,
            PRIMARY KEY (date, ticker)
        );
    """)
    conn.commit()

    # 5-2. 데이터 삽입 (ON CONFLICT 사용: 중복 데이터 방지)
    INSERT_QUERY = """
        INSERT INTO prices (date, ticker, price)
        VALUES (%s, %s, %s)
        ON CONFLICT (date, ticker) DO NOTHING;
    """

    # 5-3. Batch Insert
    # to_numpy - > ['2024-03-01' 'AAPL' 150.0]
    # execute_batch (일괄 삽입)
    data_to_insert = [tuple(row) for row in df_long.to_numpy()]
    execute_batch(cursor, INSERT_QUERY, data_to_insert)

    # 6. 변경사항 저장 및 연결 종료
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 데이터가 성공적으로 PostgreSQL에 저장되었습니다!")

except Exception as e: # pylint: disable=broad-except
    print(f"❌ 오류 발생: {e}")
