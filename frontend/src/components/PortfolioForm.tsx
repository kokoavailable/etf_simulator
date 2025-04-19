// src/components/PortfolioForm.tsx
import { useState } from 'react';
import { PortfolioInput, CreatePortfolioResponse } from '../types';
import { createPortfolio } from '../api/api';

interface PortfolioFormProps {
  onPortfolioCreated: (portfolio: CreatePortfolioResponse) => void;
}

export default function PortfolioForm({ onPortfolioCreated }: PortfolioFormProps) {
  const [input, setInput] = useState<PortfolioInput>({
    start_year: 2020,
    start_month: 1,
    invest: 100,
    trade_date: 10,
    cost: 0.001,
    calculate_month: 6, // 'caculate_month'에서 'calculate_month'로 수정
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setInput(prev => ({
      ...prev,
      [name]: name === 'cost' ? parseFloat(value) : parseInt(value, 10)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const result = await createPortfolio(input);
      onPortfolioCreated(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">포트폴리오 생성</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">시작 년도</label>
            <input
              type="number"
              name="start_year"
              value={input.start_year}
              onChange={handleChange}
              min="1900"
              max="2100"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">시작 월</label>
            <input
              type="number"
              name="start_month"
              value={input.start_month}
              onChange={handleChange}
              min="1"
              max="12"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">초기 투자금액</label>
            <input
              type="number"
              name="invest"
              value={input.invest}
              onChange={handleChange}
              min="0.01"
              step="0.01"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">매매일</label>
            <input
              type="number"
              name="trade_date"
              value={input.trade_date}
              onChange={handleChange}
              min="1"
              max="28"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">거래 수수료율</label>
            <input
              type="number"
              name="cost"
              value={input.cost}
              onChange={handleChange}
              min="0"
              max="1"
              step="0.0001"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">비중 계산 기준 개월 수</label>
            <input
              type="number"
              name="calculate_month"
              value={input.calculate_month}
              onChange={handleChange}
              min="1"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              required
            />
          </div>
        </div>
        
        <div className="mt-6">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          >
            {loading ? '처리 중...' : '포트폴리오 생성'}
          </button>
        </div>
      </form>
    </div>
  );
}