/**
 * TypeScript interfaces for coin-related data structures
 * Maps to backend Pydantic models
 */

export interface CoinBase {
  id: string;
  symbol: string;
  name: string;
}

export interface CoinResponse extends CoinBase {
  current_price: number | null;
  price_change_percentage_24h: number | null;
  last_updated: string | null;
  created_at: string;
}

export interface CoinDetail extends CoinResponse {
  market_cap: number | null;
  market_cap_rank: number | null;
  circulating_supply: number | null;
  max_supply: number | null;
  description: string | null;
  image_url: string | null;
}

export interface CoinSearchResponse extends CoinBase {
  in_portfolio: boolean;
}

export interface CoinSearchResults {
  results: CoinSearchResponse[];
  total: number;
}
