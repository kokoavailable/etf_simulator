// src/components/PortfolioChart.tsx
import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// 예시 데이터 - 실제로는 API에서 가져오게 될 것
const mockData = [
  { month: '2020-01', value: 100 },
  { month: '2020-02', value: 105 },
  { month: '2020-03', value: 95 },
  { month: '2020-04', value: 110 },
  { month: '2020-05', value: 115 },
  { month: '2020-06', value: 120 },
  { month: '2020-07', value: 125 },
  { month: '2020-08', value: 130 },
  { month: '2020-09', value: 135 },
  { month: '2020-10', value: 140 },
  { month: '2020-11', value: 145 },
  { month: '2020-12', value: 150 },
];

interface PortfolioChartProps {
  dataId?: number; // 실제 구현 시 필요할 수 있음
}

export default function PortfolioChart({ dataId }: PortfolioChartProps) {
  const [chartType, setChartType] = useState<'value' | 'return'>('value');
  
  // 실제 구현에서는 dataId를 사용하여 API에서 데이터를 가져올 수 있음
  // 지금은 목업 데이터 사용
  
  // 수익률 계산
  const returnData = mockData.map((item, index) => {
    if (index === 0) {
      return { month: item.month, value: 0 };
    }
    const returnValue = ((item.value / mockData[0].value) - 1) * 100;
    return { month: item.month, value: returnValue };
  });

  const data = chartType === 'value' ? mockData : returnData;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">포트폴리오 성과</h2>
        <div className="flex space-x-2">
          <button
            className={`px-3 py-1 rounded ${chartType === 'value' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
            onClick={() => setChartType('value')}
          >
            NAV
          </button>
          <button
            className={`px-3 py-1 rounded ${chartType === 'return' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
            onClick={() => setChartType('return')}
          >
            수익률(%)
          </button>
        </div>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip 
              formatter={(value: number) => 
                chartType === 'value' 
                  ? `${value.toFixed(2)}` 
                  : `${value.toFixed(2)}%`
              } 
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#8884d8" 
              name={chartType === 'value' ? 'NAV' : '수익률(%)'}
              activeDot={{ r: 8 }} 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}