// src/components/PortfolioDetail.tsx
import { useEffect, useState } from 'react';
import { PortfolioDetail as PortfolioDetailType } from '../types';
import { getPortfolioDetail } from '../api/api';
import Statistics from './Statistics';

interface PortfolioDetailProps {
  dataId: number | null;
}

export default function PortfolioDetail({ dataId }: PortfolioDetailProps) {
  const [portfolio, setPortfolio] = useState<PortfolioDetailType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!dataId) return;

    const fetchPortfolioDetail = async () => {
      setLoading(true);
      try {
        const data = await getPortfolioDetail(dataId);
        setPortfolio(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : '포트폴리오 상세 정보를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolioDetail();
  }, [dataId]);

  if (!dataId) {
    return null;
  }

  if (loading) {
    return <div className="text-center py-8">로딩 중...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  if (!portfolio) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">포트폴리오 #{dataId} 상세 정보</h2>
        
        <div className="bg-gray-50 p-4 rounded mb-4">
          <h3 className="text-lg font-semibold mb-2">입력 데이터</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">시작 년도</p>
              <p className="font-medium">{portfolio.input.start_year}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">시작 월</p>
              <p className="font-medium">{portfolio.input.start_month}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">초기 투자금액</p>
              <p className="font-medium">{portfolio.input.invest.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">매매일</p>
              <p className="font-medium">{portfolio.input.trade_date}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">거래 수수료율</p>
              <p className="font-medium">{portfolio.input.cost}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">비중 계산 기준 개월 수</p>
              <p className="font-medium">{portfolio.input.calculate_month}</p>
            </div>
          </div>
        </div>
      </div>
      
      <Statistics 
        stats={{
          total_return: portfolio.output.total_return,
          cagr: portfolio.output.cagr,
          vol: portfolio.output.vol,
          sharpe: portfolio.output.sharpe,
          mdd: portfolio.output.mdd
        }}
        lastWeights={portfolio.last_rebalance_weight}
      />
    </div>
  );
}
