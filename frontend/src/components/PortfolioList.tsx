// src/components/PortfolioList.tsx
import { useEffect, useState } from 'react';
import { PortfolioListItem } from '../types';
import { getPortfolioList, deletePortfolio } from '../api/api';

interface PortfolioListProps {
  onSelectPortfolio: (dataId: number) => void;
  refreshTrigger: number;
}

export default function PortfolioList({ onSelectPortfolio, refreshTrigger }: PortfolioListProps) {
  const [portfolios, setPortfolios] = useState<PortfolioListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPortfolios = async () => {
      setLoading(true);
      try {
        const data = await getPortfolioList();
        setPortfolios(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : '포트폴리오 목록을 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolios();
  }, [refreshTrigger]);

  const handleDeletePortfolio = async (dataId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (confirm('정말로 이 포트폴리오를 삭제하시겠습니까?')) {
      try {
        await deletePortfolio(dataId);
        setPortfolios(portfolios.filter(p => p.data_id !== dataId));
      } catch (err) {
        alert(err instanceof Error ? err.message : '포트폴리오 삭제에 실패했습니다.');
      }
    }
  };

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

  if (portfolios.length === 0) {
    return (
      <div className="bg-gray-100 p-6 rounded-lg text-center">
        저장된 포트폴리오가 없습니다. 새로운 포트폴리오를 생성해보세요.
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">저장된 포트폴리오 목록</h2>
      
      <div className="space-y-3">
        {portfolios.map((portfolio) => (
          <div 
            key={portfolio.data_id}
            className="bg-gray-50 p-4 rounded hover:bg-gray-100 cursor-pointer flex justify-between items-center"
            onClick={() => onSelectPortfolio(portfolio.data_id)}
          >
            <div>
              <h3 className="font-medium">포트폴리오 #{portfolio.data_id}</h3>
              <div className="text-sm text-gray-500">
                자산 수: {portfolio.last_rebalance_weight.length}
                {portfolio.last_rebalance_weight.length > 0 && (
                  <>
                    {' '}| 최대 비중 자산: {
                      portfolio.last_rebalance_weight.reduce((max, current) => 
                        current[1] > max[1] ? current : max
                      )[0]
                    }
                  </>
                )}
              </div>
            </div>
            
            <button
              onClick={(e) => handleDeletePortfolio(portfolio.data_id, e)}
              className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm"
            >
              삭제
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
