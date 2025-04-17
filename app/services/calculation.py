
"""
calculation.py 의 서비스 모듈
이 모듈은 계산 로직을 실행하고, 계산 결과를 반환하는 서비스 함수를 제공합니다.
"""

import calendar
import doctest
import statistics
from datetime import date, timedelta
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

import pandas as pd

from common.common import logger
from model.model import Price
from scheme.calculation import CalculationRequest  # 스키마 구조 참고

def get_prices_multi(db: Session,
                    tickers: List[str],
                    dates: List[date]
                    ) -> Dict[Tuple[str, date], float]:
    """
    prices 테이블에서 주어진 티커들과 날짜들에 해당하는 가격을 한 번에 조회.
    결과는 {(ticker, date): price} 형태로 리턴됨.
    """
    prices = (
        db.query(Price)
        .filter(Price.ticker.in_(tickers), Price.date.in_(dates))
        .all()
    )

    price_map = {
        (price.ticker, price.date): float(price.price) for price in prices
    }

    return price_map

# def get_price(db: Session, 
#               ticker: str, 
#               target_date: date) -> float:
#     """
#     prices 테이블에서 ticker의 target_date 가격을 조회.
#     만약 정확한 날짜 데이터가 없으면, fall back.
#     """
#     price_obj = (
#         db.query(Price)
#         .filter(Price.ticker == ticker, Price.date == target_date)
#         .first()
#     )

#     if price_obj:
#         return float(price_obj.price)
#     raise ValueError(f"{ticker} 에 대한 {target_date} 의 가격 데이터가 없습니다.")

def subtract_months(
    year: int,
    month: int,
    calc_month: int
) -> Tuple[int, int]:
    """
    주어진 년(year)과 월(month)에서, months개월 만큼 이전의 년, 월을 계산하는 함수.
    
    >>> subtract_months(2023, 2, 3)
    (2022, 11)
    >>> subtract_months(2023, 1, 15)
    (2021, 10)
    """
    total_months = year * 12 + (month - 1)
    new_total_months = total_months - calc_month
    new_year = new_total_months // 12
    new_month = new_total_months % 12 + 1
    return new_year, new_month

def adjust_to_weekday(target_date: date) -> date:
    """
    주말(토/일)인 날짜를 이전 평일로 조정하여 반환하는 함수.
    >>> adjust_to_weekday(date(2021, 3, 6))
    datetime.date(2021, 3, 5)
    >>> adjust_to_weekday(date(2021, 3, 1))
    datetime.date(2021, 2, 28)
    """
    while target_date.weekday() >= 5:  # 5: 토요일, 6: 일요일
        target_date -= timedelta(days=1)
    return target_date

def get_valid_date(year: int,
                   month: int, day: int) -> date:
    """
    입력된 날짜를 바탕으로 해당 월에 유효한 날짜를 반환하는 함수
    예를 들어, 2021년 2월 30일 -> 2021년 2월 28일

    >>> get_valid_date(2021, 2, 30)
    datetime.date(2021, 2, 28)
    """
    last_day = calendar.monthrange(year, month)[1]
    valid_day = day if day <= last_day else last_day
    return date(year, month, valid_day)


def get_trade_date(year: int, month: int, trade_day: int) -> date:
    """
    해당 년월의 매매일(존재하지 않으면 말일)을 반환.
    만약 계산된 날짜가 주말이면, 이전 평일(금요일 등)로 조정.

    >>> get_trade_date(2021, 2, 30)
    datetime.date(2021, 2, 26)
    """
    return adjust_to_weekday(get_valid_date(year, month, trade_day))

def generate_simulation_dates(start_year: int,
                              start_month: int, trade_day: int, end_date: date) -> List[date]:
    """
    시작 연, 월, 그리고 매매일을 기반으로, 
    end_date까지 매월의 유효 거래일(매매일)을 생성하는 함수.
    
    >>> generate_simulation_dates(2021, 1, 15, date(2021, 3, 31))
    >>> [datetime.date(2021, 1, 15), datetime.date(2021, 2, 12), datetime.date(2021, 3, 15)]
    """
    simulation_dates = []
    current_year = start_year
    current_month = start_month
    current_date = get_trade_date(current_year, current_month, trade_day)

    while current_date <= end_date:
        simulation_dates.append(current_date)
        # 다음 달로 이동
        if current_month == 12:
            current_year += 1
            current_month = 1
        else:
            current_month += 1
        current_date = get_trade_date(current_year, current_month, trade_day)

    return simulation_dates


def compute_monthly_returns(nav_series: List[Tuple[date, float]]) -> List[float]:
    """
    nav_series ([(날짜, nav), ...])를 입력받아, 각 기간의 월간 수익률(변화율)을 계산하여 리스트로 반환합니다.
    
    각 월의 수익률은 이전 달 NAV와 현재 달 NAV를 이용해 계산합니다.
    계산식: monthly_return = (curr_nav / prev_nav) - 1
    
    만약 prev_nav가 0이면, 해당 월 수익률은 0으로 처리합니다.
    >>> compute_monthly_returns([(date(2021, 1, 1), 100), (date(2021, 2, 1), 110), (date(2021, 3, 1), 120)])
    [0.1, 0.09090909090909083]
    """
    df = pd.DataFrame(nav_series, columns=["date", "nav"]).set_index("date")
    returns = (df["nav"] / df["nav"].shift(1)) - 1
    returns = returns.fillna(0)
    return returns.tolist()[1:]

def calculate_performance_metrics(
    nav_series: List[Tuple[date, float]],
    invest: float,
    monthly_returns: List[float]
    )-> Tuple[float, float, float, float, float]:
    """
    nav_series와 monthly_returns를 바탕으로 전체 기간 수익률, CAGR, 연 변동성, 샤프 비율, 최대 손실폭(MDD)를 계산하는 함수.
    >>> calculate_performance_metrics([(date(2021, 1, 1), 100), (date(2021, 2, 1), 110), (date(2021, 3, 1), 120)], 100, [0.1, 0.09090909090909083])
    (0.2, 0.2, 0.0, 0.0, 0.0)
    """
    # 전체 기간 수익률
    total_return = (nav_series[-1][1] / invest) - 1
    num_periods = len(nav_series)

    if num_periods > 0:
        years = num_periods / 12
        logger.info("시뮬레이션 마지막 날짜: %s", nav_series[-1])
        cagr = (nav_series[-1][1] / invest) ** (1 / years) - 1 if years > 0 else 0
        std_monthly = statistics.stdev(monthly_returns) if len(monthly_returns) > 1 else 0
        vol = std_monthly * (12 ** 0.5)
        sharpe = cagr / vol if vol != 0 else 0
    else:
        cagr = vol = sharpe = 0

    # 최대 손실폭 (MDD) 계산
    peak = -float('inf')
    mdd = 0
    for _, value in nav_series:
        peak = max(peak, value)
        drawdown = (value - peak) / peak if peak > 0 else 0
        mdd = min(mdd, drawdown)

    logger.debug(
        "[성과 지표] 투자금=%.2f | 총 수익률=%.4f | CAGR=%.4f | 변동성=%.4f | Sharpe=%.4f | MDD=%.4f",
        invest, total_return, cagr, vol, sharpe, mdd
    )

    return total_return, cagr, vol, sharpe, mdd

def handle_negative_tip(
        risky_assets: list,
        safe_assets: list) -> dict:
    """
    TIP 수익률이 음수일 때, BIL에 100% 할당하고 해당 기간 수익률을 산출합니다.
    >>> handle_negative_tip(db, date(2021, 3, 31), date(2021, 2, 28), ["SPY", "QQQ", "GLD"], "BIL")
    ({'SPY': 0.0, 'QQQ': 0.0, 'GLD': 0.0, 'BIL': 1.0}, 0)
    """
    rebalance_weight = {etf: 0.0 for etf in risky_assets}
    rebalance_weight[safe_assets[0]] = 1.0
    return rebalance_weight

def handle_positive_tip(
        price_map,
        sim_date: date,
        base_date: date,
        risky_assets: list,
        safe_assets: list,
        ) -> dict:
    """
    TIP 수익률이 양수일 때, ETF 수익률을 계산하여 리밸런싱 비중과 기간 수익률을 산출합니다.
    >>> handle_positive_tip(db, date(2021, 3, 31), date(2021, 2, 28), ["SPY", "QQQ", "GLD"], "BIL")
    ({'SPY': 0.5, 'QQQ': 0.5, 'GLD': 0.0, 'BIL': 0.0}, 0.1)
    """
    etf_returns = {}
    for etf in risky_assets:
        try:
            price_trade = price_map[(etf, sim_date)]
            price_base = price_map[(etf, base_date)]
            etf_returns[etf] = (price_trade / price_base) - 1
        except Exception:
            etf_returns[etf] = 0

    sorted_etfs = sorted(etf_returns.items(), key=lambda x: x[1], reverse=True)
    selected = sorted_etfs[:2]
    rebalance_weight = {etf: 0.0 for etf in risky_assets}
    for etf, _ in selected:
        rebalance_weight[etf] = 0.5
    rebalance_weight[safe_assets[0]] = 0.0
    return rebalance_weight

def update_nav(
        nav: float,
        current_holdings: dict,
        rebalance_weight: dict,
        etf_returns: dict,
        cost_rate: float,
        is_first = False) -> tuple:
    """
    현재 NAV를 업데이트하고, 보유 자산을 리밸런싱 합니다.
    >>> update_nav(100, {"SPY": 0.5, "QQQ": 0.5}, {"SPY": 0.5, "QQQ": 0.5, "GLD": 0.0, "BIL": 0.0}, 0.001, 0.1)
    (110.0, {'SPY': 0.5, 'QQQ': 0.5, 'GLD': 0.0, 'BIL': 0.0})
    """
    if is_first:
        target_values = {
            etf: nav * weight
            for etf, weight in rebalance_weight.items()
        }

        total_trade_amount = sum(target_values.values())

        fee = total_trade_amount * cost_rate

        final_nav = nav - fee

        target_values = {
            etf: final_nav * weight
            for etf, weight in rebalance_weight.items()
        }
        
        return final_nav, target_values
    
    # 1. 보유 자산에 ETF 수익률 적용해서 새 자산가치 계산
    updated_holdings = {
        etf: current_holdings.get(etf, 0.0) * (1 + etf_returns.get(etf, 0.0))
        for etf in rebalance_weight.keys()
    }

    # 2. 전체 자산가치 → 새로운 NAV (수익률 포함)
    updated_nav = sum(updated_holdings.values())

    logger.debug(
        "[수익률 적용] 이전 NAV=%.2f → 업데이트 NAV=%.2f",
        nav, updated_nav
    )
    logger.debug("[수익률 반영 자산] %s", updated_holdings)

    # 4. 리밸런싱 목표 자산 계산
    target_values = {etf: updated_nav * weight for etf, weight in rebalance_weight.items()}

    # 5. 총 거래금액 → 수수료 계산
    total_trade_amount = sum(
        abs(target_values[etf] - updated_holdings.get(etf, 0.0))
        for etf in target_values
    )
    fee = total_trade_amount * cost_rate


    # 6. 수수료 반영한 최종 NAV
    final_nav = updated_nav - fee

    logger.debug(
        "[리밸런싱] 목표 자산=%s | 총 거래금액=%.2f | 수수료=%.2f | 최종 NAV=%.2f",
        target_values, total_trade_amount, fee, final_nav
    )

    # 7. 최종 리밸런싱된 보유 자산 (수익률은 다음 턴에서 다시 반영됨)

    target_values = {
        etf: final_nav * weight
        for etf, weight in rebalance_weight.items()
    }
    next_holdings = target_values

    return final_nav, next_holdings

def previous_etf_return(
        price_map: dict,
        current_date: date,
        prev_date: date,
        assets: list) -> dict:
    """
    당월로부터 이전 달 etf 수익률을 계산하는 함수
    """
    etf_returns = {}

    for etf in assets:
        try:
            price_current = price_map.get((etf, current_date))
            price_prev = price_map.get((etf, prev_date))
            raw_return = (price_current / price_prev) - 1
            etf_returns[etf] = raw_return
        except Exception:
            etf_returns[etf] = 0

    return etf_returns

def simulate_strategy(calc_input:CalculationRequest, db: Session) -> dict:
    """
    입력받은 계산 파라미터와 prices 테이블 데이터를 이용해 전략 시뮬레이션 실행.

    전략 개요:
      - 매월 calc_input.trade_date를 매매일로 사용
      - 기준일 = 매매일에서 calc_input.calculate_month(계산 기준 개월) 만큼 이전 날짜
      - TIP ETF의 (매매일 대비 기준일) 수익률을 산출.
          * 양수이면, SPY, QQQ, GLD의 동일기간 수익률을 계산하여 상위 2종목에 동등하게 비중 배분.
          * 음수이면, BIL에 100% 할당.
      - 각 기간별 수익률을 반영해 NAV를 업데이트하고, 전체 성과지표(전체 수익률, CAGR, 연변동성, 샤프지수, 최대손실폭)를 산출.

    반환 dict에 input 정보, output 통계, 마지막 리밸런싱 비중 등을 포함.

    >>> simulate_strategy(CalculationRequest(start_year=2021, start_month=1, invest=100, trade_date=15, cost=0.001, calculate_month=2), db)
    {'total_return': 0.2, 'cagr': 0.2, 'vol': 0.0, 'sharpe': 0.0, 'mdd': 0.0, 'input': {'start_year': 2021, 'start_month': 1, 'invest': 100, 'trade_date': 15, 'cost': 0.001, 'calculate_month': 2}, 'rebalance_weight_series': [('2021-01-15', {'SPY': 0.5, 'QQQ': 0.5, 'GLD': 0.0, 'BIL': 0.0}), ('2021-02-12', {'SPY': 0.5, 'QQQ': 0.5, 'GLD': 0.0, 'BIL': 0.0}), ('2021-03-15', {'SPY': 0.5, 'QQQ': 0.5, 'GLD': 0.0, 'BIL': 0.0})], 'nav_series': [('2021-01-15', 100.0), ('2021-02-12', 110.0), ('2021-03-15', 120.0)}
    """
    logger.info("시뮬레이션 시작: 시작년도=%s, 시작월=%s, 투자금액=%.2f", calc_input.start_year, calc_input.start_month, calc_input.invest)

    start_year = calc_input.start_year
    start_month = calc_input.start_month
    invest = calc_input.invest
    trade_day = calc_input.trade_date
    calculate_month = calc_input.calculate_month


    end_date = date.today() # 로컬 타임존
    # 시작일로부터 calc_input.calculate_month 만큼 이전 year, month 계산
    subtracted_end_year, subtracted_end_month = subtract_months(
        end_date.year, end_date.month, calculate_month)
    
    # 오늘 부터 특정 개월 이전 날짜 계산 2021-03-31 -> 2021-02-28
    subtracted_end_date = get_valid_date(subtracted_end_year, subtracted_end_month, end_date.day)

    subtracted_start_year, subtracted_start_month = subtract_months(start_year, start_month, calculate_month
    )

    # ETF 티커 정의
    tip = "TIP"
    risky_assets = ["SPY", "QQQ", "GLD"] # 공격형 자산
    safe_assets = ["BIL"] # 방어형 자산
 
    # 시뮬레이션 날짜(매월 매매일) 리스트 생성
    simulation_dates = generate_simulation_dates(
        calc_input.start_year, calc_input.start_month,
        trade_day, end_date)
    base_dates = generate_simulation_dates(
        subtracted_start_year, subtracted_start_month,
        trade_day, subtracted_end_date)
    prev_dates = [
    get_trade_date(*subtract_months(d.year, d.month, 1), trade_day)
    for d in simulation_dates
    ]

    all_assets = risky_assets + safe_assets + [tip]
    all_dates = list(set(simulation_dates + base_dates + prev_dates))
    
    logger.debug("생성된 시뮬레이션 날짜 리스트: %s", simulation_dates)
    if not simulation_dates:
        logger.error("시뮬레이션 날짜 리스트가 비어 있습니다.")

    nav_series = []   # (날짜, nav) 저장
    rebalance_weight_series = []
    current_holdings = {etf: 0.0 for etf in risky_assets + safe_assets}  # 보유 자산 추적

    price_map = get_prices_multi(db, all_assets, all_dates)

    logger.debug("시뮬레이션 시작: 투자금=%.2f, 시작일=%s, 종료일=%s", invest, simulation_dates[0], simulation_dates[-1])
    for sim_date, base_date, prev_date in zip(simulation_dates, base_dates, prev_dates):
        # 기준일: 매매일에서 standard_month 개월 전
        logger.debug("처리 중인 날짜: %s, 기준일: %s", sim_date, base_date)

        try:
            tip_price_trade = price_map.get((tip, sim_date))
            tip_price_base = price_map.get((tip, base_date))

            if tip_price_trade is None or tip_price_base is None:
                logger.warning("TIP 가격 누락: sim_date=%s, base_date=%s", sim_date, base_date)
                continue
            
        except Exception as exc:
            logger.error("TIP 가격 조회 오류: %s",
                         exc, exc_info=True)
            continue
        
 
        tip_return = (tip_price_trade / tip_price_base) - 1
        
        logger.debug("TIP 가격: 기준=%.2f, 거래=%.2f, 수익률=%.4f", tip_price_base, tip_price_trade, tip_return)

        if tip_return > 0:
            try:
                rebalance_weight = handle_positive_tip(
                    price_map, sim_date, base_date, risky_assets, safe_assets)
            except Exception as exc:
                logger.error("날짜 %s 에서 positive TIP 처리 중 오류 발생: %s",
                             sim_date, exc, exc_info=True)
                continue
        else:
            # TIP 수익률 음수이면 BIL 전환
            try:
                rebalance_weight = handle_negative_tip(
                    risky_assets, safe_assets)
            except Exception as exc:
                logger.error("날짜 %s 에서 negative TIP 처리 중 오류 발생: %s",
                             sim_date, exc, exc_info=True)
                continue
        try:
            logger.debug("리밸런싱 비중: %s", rebalance_weight)

            previous_nav = nav_series[-1][1] if nav_series else invest

            if previous_nav == 0:
                raise ValueError("초기 NAV가 0입니다. 투자금(invest)이 0이 아닌지 확인하세요.")
            
            is_first = len(nav_series) == 0
            etf_returns = previous_etf_return(price_map, sim_date, prev_date, risky_assets + safe_assets)
            logger.debug("ETF 수익률: %s", etf_returns)

            logger.debug("NAV 업데이트 전: NAV=%.2f | 보유자산=%s", previous_nav, current_holdings)
            nav, next_holdings = update_nav(
                previous_nav,
                current_holdings,
                rebalance_weight,
                etf_returns,
                calc_input.cost,
                is_first=is_first
            )

            current_holdings = next_holdings

        except Exception as exc:
            logger.error("날짜 %s 에서 NAV 업데이트 중 오류 발생: %s",
                         sim_date, exc, exc_info=True)
            continue


        logger.debug("날짜 %s: 업데이트 후 NAV=%.2f, 보유 자산=%s",
                     sim_date, nav, next_holdings)
        rebalance_weight_series.append((sim_date.isoformat(), list(rebalance_weight.items())))
        nav_series.append((sim_date.isoformat(), nav))

    if not nav_series:
        logger.error("시뮬레이션 루프 종료 후 NAV 시리즈가 비어 있습니다.")
        raise ValueError("NAV 시리즈가 비어 있습니다.")
    logger.debug("최종 NAV 시리즈: %s, 길이:%s", nav_series, len(nav_series))
    monthly_returns = compute_monthly_returns(nav_series)
    logger.debug("[월간 수익률]: %s, [길이]:%s", monthly_returns, len(monthly_returns))
    try:
        total_return, cagr, vol, sharpe, mdd = calculate_performance_metrics(
        nav_series,
        invest,
        monthly_returns
    )
    except Exception as exc:
        logger.error("성과 지표 계산 중 오류 발생: %s", exc, exc_info=True)
        raise

    logger.info("시뮬레이션 종료: 총 NAV=%.2f, 전체수익률=%.4f, CAGR=%.4f", nav, total_return, cagr)


    return {
        "total_return": total_return,
        "cagr": cagr,
        "vol": vol,
        "sharpe": sharpe,
        "mdd": mdd,
        "input": calc_input.dict(),
        "rebalance_weight_series": rebalance_weight_series, 
        "nav_series": nav_series 
    }

if __name__ == "__main__":
    import doctest
    doctest.testmod()
