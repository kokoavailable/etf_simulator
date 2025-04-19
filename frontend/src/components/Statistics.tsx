// src/components/Statistics.tsx
import { PortfolioStats, RebalanceWeight } from '../types';

interface StatisticsProps {
  stats: PortfolioStats;
  lastWeights: RebalanceWeight[];
}

export default function Statistics({ stats, lastWeights }: StatisticsProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">포트폴리오 통계</h2>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <h3 className="text-lg font-semibold mb-2">성과 지표</h3>
          <div className="bg-gray-50 p-4 rounded">
            <div className="flex justify-between mb-2">
              <span>전체 기간 수익률</span>
              <span className="font-bold">{(stats.total_return * 100).toFixed(2)}%</span>
            </div>
            <div className="flex justify-between mb-2">
              <span>연환산수익률</span>
              <span className="font-bold">{(stats.cagr * 100).toFixed(2)}%</span>
            </div>
            <div className="flex justify-between mb-2">
              <span>연변동성</span>
              <span className="font-bold">{(stats.vol * 100).toFixed(2)}%</span>
            </div>
            <div className="flex justify-between mb-2">
              <span>샤프지수</span>
              <span className="font-bold">{stats.sharpe.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>최대손실폭</span>
              <span className="font-bold text-red-600">{(stats.mdd * 100).toFixed(2)}%</span>
            </div>
          </div>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold mb-2">마지막 리밸런싱 비중</h3>
          <div className="bg-gray-50 p-4 rounded max-h-60 overflow-y-auto">
            {lastWeights.map(([asset, weight], index) => (
              <div key={index} className="flex justify-between mb-2">
                <span>{asset}</span>
                <span className="font-bold">{(weight * 100).toFixed(2)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
