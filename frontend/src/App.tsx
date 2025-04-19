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
      <div className="container mx-auto px-4">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">포트폴리오 리밸런싱 분석</h1>
          <p className="mt-2 text-gray-600">
            투자 포트폴리오 성과 분석 및 리밸런싱 전략 평가
          </p>
        </header>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
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
