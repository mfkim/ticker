export interface StockRanking {
  Symbol: string;
  Name: string;
  MarketCap: number | null;
  Close: number;
  ChangeRate: number | null;
}
