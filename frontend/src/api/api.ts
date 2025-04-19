// src/api/api.ts
import { PortfolioInput, CreatePortfolioResponse, PortfolioListItem, PortfolioDetail, DeleteResponse } from '../types';

const API_URL = 'http://localhost:8000'; // FastAPI 서버 URL

export const createPortfolio = async (input: PortfolioInput): Promise<CreatePortfolioResponse> => {
  const response = await fetch(`${API_URL}/v1/api/calculation/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  });
  
  if (!response.ok) {
    throw new Error('Failed to create portfolio');
  }
  
  return response.json();
};

export const getPortfolioList = async (): Promise<PortfolioListItem[]> => {
  const response = await fetch(`${API_URL}/v1/api/calculation/calculations`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch portfolio list');
  }
  
  return response.json();
};

export const getPortfolioDetail = async (dataId: number): Promise<PortfolioDetail> => {
  const response = await fetch(`${API_URL}/v1/api/calculation/calculations/${dataId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch portfolio detail for ID: ${dataId}`);
  }
  
  return response.json();
};

export const deletePortfolio = async (dataId: number): Promise<DeleteResponse> => {
  const response = await fetch(`${API_URL}/v1/api/calculation/calculations/${dataId}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to delete portfolio with ID: ${dataId}`);
  }
  
  return response.json();
};
