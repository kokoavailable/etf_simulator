"""
crud.calculation 모듈

이 계층은 계산 결과를 메인 DB에 저장하거나 조회하는 기능을 제공합니다.

"""

from typing import List
from sqlalchemy.orm import Session
from model.model import Calculation
from scheme.calculation import CalculationRequest

def create_calculation(
    db: Session,
    calc_input: CalculationRequest,
    rebanlance_weight_series: list,
    nav_series: list
) -> Calculation:
    """
    계산 결과를 DB에 저장하고, 저장된 레코드를 반환합니다.
    """
    record = Calculation(
        start_year=calc_input.start_year,
        start_month=calc_input.start_month,
        invest=calc_input.invest,
        trade_date=calc_input.trade_date,
        cost=calc_input.cost,
        calculate_month=calc_input.calculate_month,
        last_rebalance_weight=rebanlance_weight_series[-1],
        rebalance_weights_series=rebanlance_weight_series,
        nav_sums_series=nav_series
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_calculation_by_id(db: Session, data_id: int) -> Calculation:
    """
    data_id에 해당하는 Calculation 레코드를 조회합니다.
    """
    return db.query(Calculation).filter(Calculation.data_id == data_id).first()

def get_all_calculations(db: Session) -> List[Calculation]:
    """
    모든 Calculation 레코드를 조회합니다.
    """
    return db.query(Calculation).all()

def delete_calculation(db: Session, data_id: int) -> Calculation:
    """
    data_id에 해당하는 Calculation 레코드를 삭제하고, 삭제된 레코드를 반환합니다.
    """
    record = get_calculation_by_id(db, data_id)
    if record:
        db.delete(record)
        db.commit()
    return record
