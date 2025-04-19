export interface PortfolioInput {
    start_year: number;
    start_month: number;
    invest: number;
    trade_date: number;
    cost: number;
    calculate_month: number; // 'caculate_month'에서 'calculate_month'로 수정
  }
  
  export type Asset = string;
  export type Weight = number;
  export type RebalanceWeight = [Asset, Weight];
  
  export interface PortfolioStats {
    total_return: number;
    cagr: number;
    vol: number;
    sharpe: number;
    mdd: number;
  }
  
  // API-A 응답 타입
  export interface CreatePortfolioResponse {
    data_id: number;
    output: PortfolioStats;
    last_rebalance_weight: RebalanceWeight[];
  }
  
  // API-B 응답 타입
  export interface PortfolioListItem {
    data_id: number;
    last_rebalance_weight: RebalanceWeight[];
  }
  
  // API-C 응답 타입
  export interface PortfolioDetail {
    input: PortfolioInput;
    output: {
      data_id: number;
      total_return: number;
      cagr: number;
      vol: number;
      sharpe: number;
      mdd: number;
    };
    last_rebalance_weight: RebalanceWeight[];
  }
  
  // API-D 응답 타입
  export interface DeleteResponse {
    data_id: number;
  }
  