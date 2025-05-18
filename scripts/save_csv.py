"""
데이터 시트를 받아서 PostgreSQL에 저장하는 스크립트
"""


import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from common import DB_PARAMS

CSV_FILE = "price_data.csv"
df = pd.read_csv(CSV_FILE) # 판다스로 csv 파일을 읽어 데이터 프레임으로 변환한다.

# 3. 데이터 변환 (Wide → Long Format)
# date는 고정(id_vars), 나머지 종목 컬럼(AAPL, MSFT, AMZN 등)을
# 'ticker' 컬럼의 값으로 모으고, 각 셀의 실제 값은 'price' 컬럼에 저장한다.
# 즉, Wide(가로) → Long(세로) 포맷으로 변환.
df_long = df.melt(id_vars=["date"], var_name="ticker", value_name="price")

# 4. 데이터 타입 변환
# csv 파일에서 읽어온 데이터는 문자열로 되어있기 때문에,
# 날짜(date) 컬럼을 적절한 데이터 타입으로 변환한다.
# 문자열의 날짜 형식을 보고 format 을 지정해줄 수도 있다.
df_long["date"] = pd.to_datetime(df_long["date"])  # 날짜 변환

# 5. PostgreSQL 연결 및 데이터 삽입
try:
    conn = psycopg2.connect(**DB_PARAMS) # 딕셔너리를 키워드인자로 풀어서 함수에 전달하라.
    cursor = conn.cursor() # 디비를 조작하기 위한 커서를 생성한다.
    # 내장 커넥션 풀등의 기능은 없기 때문에 연결이 생성된 상태이며,
    # 커서를 사용한 후에는 반드시 close() 메서드를 호출하여 리소스를 해제해야 한다.

    # 5-1. 테이블이 존재하지 않으면 생성
    # 키 충돌시 무시하는 옵션을 사용한다.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            date DATE NOT NULL,
            ticker VARCHAR(10) NOT NULL,
            price NUMERIC(13,4) NOT NULL,
            PRIMARY KEY (date, ticker)
        );
    """)
    conn.commit() # 테이블 생성은 즉시 반영해야 하므로 커밋한다.
    # 일단 커밋을 하면 롤백이 불가능하다. execute()자체가 flush()의 기능을한다

    # 5-2. 데이터 삽입 (ON CONFLICT 사용: 중복 데이터 방지)
    INSERT_QUERY = """
        INSERT INTO prices (date, ticker, price)
        VALUES %s
        ON CONFLICT (date, ticker) DO NOTHING;
    """

    # 5-3. Batch Insert (일괄 삽입)
    # - SQL execute_batch 등에 파라미터로 넘길 때 각 row는 튜플(혹은 리스트)이어야 함
    # - 리스트도 되지만, 관례적으로 튜플(tuple) 많이 씀 (immutable, SQL 드라이버가 최적화)
    # - df.values는 deprecated(향후 사라질 예정) → 권장하지 않음
    # - df.itertuples()는 row를 바로 튜플로 반환하나, 순회 속도가 to_numpy()보다 느릴 수 있음
    # - df.to_numpy()는 C기반 구현(가장 빠르고, 공식 추천 방식)
    #     → np.array(row)를 tuple(row)로 변환해서 넘기는 게 관례
    # - 즉, 실전에서는 [tuple(row) for row in df.to_numpy()] 패턴이 가장 많이 쓰임
    data_to_insert = [tuple(row) for row in df_long.to_numpy()]
    # 여러개의 row를 한번에 쿼리 전송한다.
    # execute_many()도 한번의 함수 호출로 한번에 전달 가능하지만 느리다.
    # execute_values()는 모든 raw를 한번에 values 로 변환해서 정말 한번만 수행한다.
    # execute_batch()는 최적화로 many보다는 빠르나 내부적으로는 여러번 수행한다.
    execute_values(cursor, INSERT_QUERY, data_to_insert)

    # 6. 변경사항 저장 및 연결 종료
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 데이터가 성공적으로 PostgreSQL에 저장되었습니다!")

except Exception as e: # pylint: disable=broad-except
    print(f"❌ 오류 발생: {e}")
