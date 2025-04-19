import React, { useState, useEffect } from 'react';
import { calculateStrategy, getCalculations, getCalculationDetail, deleteCalculation } from '../api/api';
import CalculationForm from '../components/CalculationForm';
import CalculationList from '../components/CalculationList';
import CalculationDetail from '../components/CalculationDetail';

export default function PortfolioApp() {
  const [activeTab, setActiveTab] = useState<'calculate' | 'list' | 'details'>('calculate');
  const [formData, setFormData] = useState({
    start_year: 2020,
    start_month: 1,
    invest: 100,
    trade_date: 10,
    cost: 0.001,
    caculate_month: 6
  });

  const [dataList, setDataList] = useState([]);
  const [currentData, setCurrentData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]:
        ['start_year', 'start_month', 'trade_date', 'caculate_month'].includes(name)
          ? parseInt(value)
          : parseFloat(value)
    });
  };

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      const res = await calculateStrategy(formData);
      setCurrentData(res.data);
      setActiveTab('details');
      setSuccess('Calculation successful!');
    } catch (err) {
      setError('Failed to calculate. Please check your input.');
    } finally {
      setLoading(false);
    }
  };

  const loadDataList = async () => {
    try {
      setLoading(true);
      const res = await getCalculations();
      setDataList(res.data);
    } catch (err) {
      setError('Failed to load saved calculations.');
    } finally {
      setLoading(false);
    }
  };

  const handleView = async (id: number) => {
    try {
      setLoading(true);
      const res = await getCalculationDetail(id);
      setCurrentData(res.data);
      setActiveTab('details');
    } catch (err) {
      setError(`Failed to load detail for ID ${id}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm(`Are you sure you want to delete ID ${id}?`)) return;

    try {
      setLoading(true);
      await deleteCalculation(id);
      setSuccess(`Deleted ID ${id}`);
      setCurrentData(null);
      loadDataList();
      setActiveTab('list');
    } catch (err) {
      setError(`Failed to delete ID ${id}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'list') {
      loadDataList();
    }
  }, [activeTab]);

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-50 rounded-lg shadow-lg">
      <h1 className="text-2xl font-bold mb-6 text-blue-800">📊 Portfolio Rebalancing Tool</h1>

      {/* Tabs */}
      <div className="flex mb-6 border-b">
        <button
          className={`px-4 py-2 ${activeTab === 'calculate' ? 'bg-blue-500 text-white' : 'bg-gray-200'} rounded-t-lg mr-2`}
          onClick={() => setActiveTab('calculate')}
        >
          Calculate
        </button>
        <button
          className={`px-4 py-2 ${activeTab === 'list' ? 'bg-blue-500 text-white' : 'bg-gray-200'} rounded-t-lg mr-2`}
          onClick={() => setActiveTab('list')}
        >
          Saved Calculations
        </button>
        {currentData && activeTab === 'details' && (
          <button className="px-4 py-2 bg-blue-500 text-white rounded-t-lg">
            Details: ID {currentData.output?.data_id}
          </button>
        )}
      </div>

      {/* Notifications */}
      {error && <div className="bg-red-100 text-red-700 px-4 py-3 mb-4 rounded">{error}</div>}
      {success && <div className="bg-green-100 text-green-700 px-4 py-3 mb-4 rounded">{success}</div>}
      {loading && (
        <div className="flex justify-center items-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}

      {/* Views */}
      {activeTab === 'calculate' && (
        <CalculationForm
          formData={formData}
          onChange={handleInputChange}
          onSubmit={handleCalculate}
          loading={loading}
        />
      )}

      {activeTab === 'list' && (
        <CalculationList dataList={dataList} onView={handleView} onDelete={handleDelete} />
      )}

      {activeTab === 'details' && currentData && (
        <CalculationDetail data={currentData} onBack={() => setActiveTab('list')} onDelete={handleDelete} />
      )}
    </div>
  );
}