"""
api.v1.endpoints.calculation 모듈

이 모듈은 투자 전략 계산과 관련된 API 엔드포인트를 제공합니다.  
사용자가 제공한 입력 데이터를 기반으로 투자 전략을 시뮬레이션하고,  
결과를 데이터베이스에 저장하거나 조회할 수 있습니다.

📌 제공하는 API:
- `POST /v1/api/calculation/calculate`: 투자 전략을 시뮬레이션하고 결과 저장
- `GET /v1/api/calculation/{data_id}`: 특정 계산 결과 조회
- `GET /v1/api/calculation`: 모든 계산 결과 목록 조회
- `DELETE /v1/api/calculation/{data_id}`: 특정 계산 결과 삭제
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from common.common import get_db
from crud.calculation import (
    create_calculation,
    get_calculation_by_id,
    get_all_calculations,
    delete_calculation
)

from services.calculation import (
    simulate_strategy,
    compute_monthly_returns,
    calculate_performance_metrics
)
from scheme.calculation import (
    CalculationRequest,
    CalculationOutput,
    CalculationResponse,
    CalculationListItem,
    CalculationDetailResponse,
    CalculationDeleteResponse,
    CalculationResultOutput
)

router = APIRouter()

# API - A 입력을 받아 계산 로직을 실행, DB저장, 저장된 data_id 와 함께 반환
@router.post("/calculate", response_model=CalculationResponse)
def calculate_strategy(calc_input: CalculationRequest, db:Session = Depends(get_db)):
    """
    투자 전략을 시뮬레이션하고 결과를 저장하는 API 엔드포인트
    """
    result = simulate_strategy(calc_input, db)

    calculation_output = CalculationOutput(
        total_return=result["total_return"],
        cagr=result["cagr"],
        vol=result["vol"],
        sharpe=result["sharpe"],
        mdd=result["mdd"]
    )

    record = create_calculation(db, calc_input,
                                result["rebalance_weight_series"],
                                result["nav_series"])

    return CalculationResponse(
        data_id=record.data_id,
        output=calculation_output,
        last_rebalance_weight=result["rebalance_weight_series"][-1][1]
    )

# API - B 저장된 data_id 목록과 마지막 리밸런싱 비중을 반환하는 API
@router.get("/calculations", response_model=List[CalculationListItem])
def get_calculations_list(db: Session = Depends(get_db)):
    """
    모든 계산 결과 목록을 조회하는 API 엔드포인트
    """
    records = get_all_calculations(db)
    return [
        CalculationListItem(
            data_id=r.data_id,
            last_rebalance_weight=r.last_rebalance_weight[1]
        )
        for r in records
    ]

# API - C data_id에 해당하는 저장 항목을 불러와 계산한 통계값과 마지막 리밸런싱 비중을 반환하는 API
@router.get("/calculations/{data_id}", response_model=CalculationDetailResponse)
def get_calculation_detail(data_id: int, db: Session = Depends(get_db)):
    """
    data_id에 해당하는 계산 결과를 조회하는 API 엔드포인트
    """
    calc_record = get_calculation_by_id(db, data_id)
    if not calc_record:
        raise HTTPException(status_code=404, detail="Calculation record not found")

    input_data = CalculationRequest(
        start_year=calc_record.start_year,
        start_month=calc_record.start_month,
        invest=calc_record.invest,
        trade_date=calc_record.trade_date,
        cost=calc_record.cost,
        calculate_month=calc_record.calculate_month
    )

    try:
        nav_sums_series = calc_record.nav_sums_series
    except AttributeError:
        pass

    monthly_returns = compute_monthly_returns(nav_sums_series)

    total_return, cagr, vol, sharpe, mdd = calculate_performance_metrics(
        nav_sums_series,
        calc_record.invest,
        monthly_returns
    )

    output_data = CalculationResultOutput(
        data_id=calc_record.data_id,
        total_return=total_return,
        cagr=cagr,
        vol=vol,
        sharpe=sharpe,
        mdd=mdd
    )


    return CalculationDetailResponse(
        input = input_data,
        output = output_data,
        last_rebalance_weight = calc_record.last_rebalance_weight[1])


# API - D 삭제된 data_id만 반환
@router.delete("/calculations/{data_id}", response_model=CalculationDeleteResponse)
def delete_calculations_entry(data_id: int, db: Session = Depends(get_db)):
    """
    data_id에 해당하는 계산 결과를 삭제하는 API 엔드포인트
    """
    record = delete_calculation(db, data_id)
    if not record:
        raise HTTPException(status_code=404, detail="Calculation record not found")

    return CalculationDeleteResponse(data_id=data_id)
