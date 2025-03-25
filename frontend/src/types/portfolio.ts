/**
 * TypeScript interfaces for portfolio-related data structures
 * Maps to backend Pydantic models
 */

import { CoinResponse } from './coin';

export interface PortfolioEntryBase {
  coin_id: string;
  amount: number;
}

export interface PortfolioEntryCreate extends PortfolioEntryBase {}

export interface PortfolioEntryUpdate {
  amount: number;
}

export interface PortfolioEntryResponse extends PortfolioEntryBase {
  id: number;
  updated_at: string;
  created_at: string;
  coin: CoinResponse;
  current_value_usd: number | null;
}

export interface PortfolioSummary {
  total_value_usd: number;
  entries: PortfolioEntryResponse[];
  total_coins: number;
  total_24h_change_percentage: number | null;
}
