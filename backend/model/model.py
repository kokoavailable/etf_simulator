"""
model.model 모듈

이 모듈은 SQLAlchemy ORM을 사용하여 데이터베이스 테이블을 정의하는 모델을 포함합니다.

클래스:
    - Price: 가격 정보를 저장하는 테이블
    - Calculation: 투자 전략 계산 결과를 저장하는 테이블
"""


from sqlalchemy import (
    Column, 
    Integer, 
    Float, 
    JSON, 
    DateTime, 
    String, 
    Numeric, 
    Date, 
    text
)
from sqlalchemy.orm import declarative_base

# SQLAlchemy ORM 모델의 부모 클래스
# 이 클래스를 상속받는 모든 ORM 모델은 자동으로 metadata에 등록됨
Base = declarative_base()


class Price(Base): # pylint: disable=too-few-public-methods
    """
    Price: 가격 정보를 저장하는 테이블
    """
    __tablename__ = "prices"

    date = Column(Date, primary_key=True)
    ticker = Column(String(10), primary_key=True)
    price = Column(Numeric(13,4))

class Calculation(Base): # pylint: disable=too-few-public-methods
    """
    Calculation: 투자 전략 계산 결과를 저장하는 테이블
    """
    __tablename__ = "calculations"

    data_id = Column(Integer, primary_key=True, autoincrement=True)

    start_year = Column(Integer, nullable=False)
    start_month = Column(Integer, nullable=False)
    invest = Column(Float, nullable=False)
    trade_date = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    calculate_month = Column(Integer, nullable=False)
    last_rebalance_weight = Column(JSON, nullable=False)

    rebalance_weights_series = Column(JSON, nullable=False)
    nav_sums_series = Column(JSON, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
