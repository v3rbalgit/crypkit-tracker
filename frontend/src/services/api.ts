import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  CoinBase,
  CoinDetail,
  CoinSearchResults,
} from '../types/coin';
import {
  PortfolioEntryResponse,
  PortfolioSummary,
} from '../types/portfolio';

// Use environment variable for API URL if available, otherwise default to '/api'
const API_URL = process.env.REACT_APP_API_BASE_URL || '/api';

// Create an axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Log which API URL is being used (for debugging purposes)
console.log('Using API URL:', API_URL);

interface CoinAPI {
  getCoins: () => Promise<CoinBase[]>;
  searchCoins: (query: string, limit?: number) => Promise<CoinSearchResults>;
  getCoin: (coinId: string) => Promise<CoinDetail>;
}

interface PortfolioAPI {
  getPortfolio: () => Promise<PortfolioEntryResponse[]>;
  getPortfolioSummary: () => Promise<PortfolioSummary>;
  addCoin: (coinId: string, amount: number) => Promise<PortfolioEntryResponse>;
  updateEntry: (entryId: number, amount: number) => Promise<PortfolioEntryResponse>;
  removeEntry: (entryId: number) => Promise<{ detail: string }>;
  refreshPrices: () => Promise<{ detail: string }>;
}

// Coins API
export const coinApi: CoinAPI = {
  // Get a list of all coins
  getCoins: async () => {
    const response = await api.get<CoinBase[]>('/coins');
    return response.data;
  },

  // Search for coins with advanced filters
  searchCoins: async (query: string, limit = 100) => {
    const response = await api.get<CoinSearchResults>('/coins/search/', {
      params: { query, limit }
    });
    return response.data;
  },

  // Get details for a specific coin
  getCoin: async (coinId: string) => {
    const response = await api.get<CoinDetail>(`/coins/${coinId}`);
    return response.data;
  },
};

// Portfolio API
export const portfolioApi: PortfolioAPI = {
  // Get all portfolio entries
  getPortfolio: async () => {
    const response = await api.get<PortfolioEntryResponse[]>('/portfolio');
    return response.data;
  },

  // Get portfolio summary
  getPortfolioSummary: async () => {
    const response = await api.get<PortfolioSummary>('/portfolio/summary');
    return response.data;
  },

  // Add a coin to the portfolio
  addCoin: async (coinId: string, amount: number) => {
    const response = await api.post<PortfolioEntryResponse>('/portfolio', {
      coin_id: coinId,
      amount,
    });
    return response.data;
  },

  // Update a portfolio entry
  updateEntry: async (entryId: number, amount: number) => {
    const response = await api.put<PortfolioEntryResponse>(`/portfolio/${entryId}`, {
      amount,
    });
    return response.data;
  },

  // Remove a coin from the portfolio
  removeEntry: async (entryId: number) => {
    const response = await api.delete<{ detail: string }>(`/portfolio/${entryId}`);
    return response.data;
  },

  // Refresh all coin prices
  refreshPrices: async () => {
    const response = await api.post<{ detail: string }>('/portfolio/refresh-prices');
    return response.data;
  },
};

export default { coinApi, portfolioApi };
