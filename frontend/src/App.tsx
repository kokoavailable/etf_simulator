// src/App.tsx
import { useState } from 'react';
import PortfolioForm from './components/PortfolioForm';
import PortfolioList from './components/PortfolioList';
import PortfolioDetail from './components/PortfolioDetail';
import Statistics from './components/Statistics';
import PortfolioChart from './components/PortfolioChart';
import { CreatePortfolioResponse } from './types';

export default function App() {
  const [selectedDataId, setSelectedDataId] = useState<number | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [lastCreatedPortfolio, setLastCreatedPortfolio] = useState<CreatePortfolioResponse | null>(null);

  const handlePortfolioCreated = (portfolio: CreatePortfolioResponse) => {
    setLastCreatedPortfolio(portfolio);
    setRefreshTrigger(prev => prev + 1);
  };

  const handleSelectPortfolio = (dataId: number) => {
    setSelectedDataId(dataId);
    setLastCreatedPortfolio(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      {/* div의 높이를 화면 전체로 설정하고 배경색을 연한 회색으로 설정, y 축 패딩 0 */}
      <div className="container mx-auto px-4">
        {/* 컨테이너의 너비를 화면에 맞게 설정하고 좌우 패딩을 추가 1em (현재나 상속받은 부모의 폰트 사이즈. 테일윈드는 16px = 1em)*/}
        <header className="mb-8 text-center">
          {/* mb-8: 아래쪽 마진(여백) 2rem(=32px) / text-center: 가운데 정렬 */}
          <h1 className="text-3xl font-bold text-gray-900">포트폴리오 리밸런싱 분석</h1>
          {/* text-3xl: 글씨 크기 크게(1.875rem=30px) / font-bold: 굵게 / text-gray-900: 거의 검정색 텍스트 */}
          <p className="mt-2 text-gray-600">
            {/* mt-2: 위쪽 마진(여백) 0.5rem(=8px) / text-gray-600: 회색 텍스트 */}
            투자 포트폴리오 성과 분석 및 리밸런싱 전략 평가
          </p>
        </header>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* grid-cols-1: 1열 / lg:grid-cols-2: lg(=large) 사이즈 이상에서 2열로 변경 / gap-8: 열 사이의 간격 2rem(=32px) */}
          
          {/* 포트폴리오 생성 및 목록 */}
          <div className="space-y-8">
            <PortfolioForm onPortfolioCreated={handlePortfolioCreated} />
            
            {lastCreatedPortfolio && (
              <div className="bg-green-50 border border-green-400 p-4 rounded">
                <h3 className="text-lg font-semibold text-green-800 mb-2">
                  포트폴리오가 성공적으로 생성되었습니다! (ID: {lastCreatedPortfolio.data_id})
                </h3>
                <Statistics 
                  stats={lastCreatedPortfolio.output}
                  lastWeights={lastCreatedPortfolio.last_rebalance_weight}
                />
              </div>
            )}
            
            <PortfolioList 
              onSelectPortfolio={handleSelectPortfolio} 
              refreshTrigger={refreshTrigger} 
            />
          </div>
          
          <div className="space-y-8">
            <PortfolioDetail dataId={selectedDataId} />
            {selectedDataId && <PortfolioChart dataId={selectedDataId} />}
          </div>
        </div>
      </div>
    </div>
  );
}
