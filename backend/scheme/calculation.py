"""
calculation.py

이 파일은 계산 관련 Pydantic 모델을 정의합니다.

API - A: 통계값 계산을 위한 input과 저장한 data_id와 계산한 통계값을 반환하는 API
API - B: data_id와 마지막 리밸런싱 비중 목록을 반환하는 API
API - C: data_id에 해당하는 저장 항목을 불러와 계산한 통계값과 마지막 리밸런싱 비중을 반환하는 API
API - D: 삭제된 data_id만 반환하는 API
"""

from typing import List, Tuple
from pydantic import BaseModel, field_validator

# 통계값 베이스 모델 (전체 수익률, CAGR, 변동성, 샤프지수, MDD)
class CalculationOutput(BaseModel):
    """
    통계값 (전체 수익률, CAGR, 변동성, 샤프지수, MDD) 모델
    """
    total_return: float
    cagr: float
    vol: float
    sharpe: float
    mdd: float

### API - A

# 통계값 계산을 위한 input
class CalculationRequest(BaseModel):
    """
    통계값 계산을 위한 입력값 모델
    """
    start_year: int
    start_month: int
    invest: float
    trade_date: int
    cost: float
    calculate_month: int

    @field_validator("start_year")
    def validate_start_year(cls, value):# pylint: disable=no-self-argument
        """유효 주식시장 시작년도 검증"""
        if not 1900 <= value <= 2100:
            raise ValueError("start_year must be between 1900 and 2100")
        return value

    @field_validator("start_month")
    def validate_start_month(cls, value):# pylint: disable=no-self-argument
        """유효 주식시장 시작월 검증"""
        if not 1 <= value <= 12:
            raise ValueError("start_month must be between 1 and 12")
        return value

    @field_validator("invest")
    def validate_invest(cls, value):# pylint: disable=no-self-argument
        """투자금액 검증"""
        if value <= 0:
            raise ValueError("invest must be a positive value")
        return value

    @field_validator("trade_date")
    def validate_trade_date(cls, value):# pylint: disable=no-self-argument
        """거래일 검증"""
        if not 1 <= value <= 28:
            raise ValueError("trade_date must be between 1 and 28")
        return value

    @field_validator("cost")
    def validate_cost(cls, value):# pylint: disable=no-self-argument
        """거래 수수료율 검증"""
        # cost는 거래 수수료율로 0 이상 1 이하의 값이어야 합니다.
        if not 0 <= value <= 1:
            raise ValueError("cost must be between 0 and 1")
        return value

    @field_validator("calculate_month")
    def validate_calculate_month(cls, value):# pylint: disable=no-self-argument
        """계산할 개월 수 검증"""
        if value <= 0:
            raise ValueError("calculate_month must be a positive integer")
        return value

# 저장한 data_id와 계산한 통계값을 반환하는 API
class CalculationResponse(BaseModel):
    """
    계산 결과 반환 API 모델
    """
    data_id: int
    output: CalculationOutput
    last_rebalance_weight: List[Tuple[str, float]]


### API - B

# data_id와 마지막 리밸런싱 비중 목록. endpoint 에서 리스트로 반환하는 API
class CalculationListItem(BaseModel):
    """
    저장된 계산 목록 반환 API 모델
    """
    data_id: int
    last_rebalance_weight: List[Tuple[str, float]]


### API - C data_id에 해당하는 저장 항목을 불러와 계산한 통계값과  마지막 리밸런싱 비중을 반환하는 API


# BaseCalculationOutput에 data_id를 추가
class CalculationResultOutput(CalculationOutput):
    """
    data_id 를 추가한 통계값 (전체 수익률, CAGR, 변동성, 샤프지수, MDD) 모델
    """
    data_id: int

# data_id에 해당하는 저장 항목을 불러와 계산한 통계값과  마지막 리밸런싱 비중을 반환하는 API
class CalculationDetailResponse(BaseModel):
    """
    저장된 계산 결과 상세 반환 API 모델
    """
    input: CalculationRequest
    output: CalculationResultOutput
    last_rebalance_weight: List[Tuple[str, float]]


### API - D


# 삭제된 data_id만 반환
class CalculationDeleteResponse(BaseModel):
    """
    삭제된 계산 결과 반환 API 모델
    """
    data_id: int
