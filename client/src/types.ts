export interface StockRanking {
  Symbol: string;
  Name: string;
  MarketCap: number | null;
  Close: number;
  ChangeRate: number | null;
}

export interface TickerInfo {
  Symbol: string;
  Name: string;
  Sector: string | null;
  Industry: string | null;
  MarketCap: number | null;
}

export interface StockPrice {
  Date: string;
  Close: number;
  Open: number | null;
  High: number | null;
  Low: number | null;
  Volume: number | null;
  ChangeRate: number | null;
  MA_20: number | null;
  RSI_14: number | null;
}

export interface StockDetailResponse {
  info: TickerInfo;
  prices: StockPrice[];
}
