import {useEffect, useState} from "react";
import StockCard from "./StockCard";
import type {StockRanking} from "../types";

export default function StockDashboard() {
  const [stocks, setStocks] = useState<StockRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    // API
    fetch("/api/v1/stocks/ranking?limit=100")
      .then((res) => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
      })
      .then((data) => {
        setStocks(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setError(true);
        setLoading(false);
      });
  }, []);

  // 에러 처리
  if (error) {
    return (
      <div className="text-center py-20 text-rh-red">
        <h2 className="text-2xl font-bold">Failed to load market data.</h2>
        <p className="text-rh-subtext">Please ensure the backend server is running.</p>
      </div>
    );
  }

  return (
    <section>
      {/* 섹션 헤더 */}
      <div className="mb-8 flex items-end justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">Standard and Poor's 500</h2>
          <p className="text-rh-subtext mt-1">Top 100 Companies by Market Cap</p>
        </div>
      </div>

      {/* 그리드 레이아웃 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">

        {/* 로딩 중 */}
        {loading
          ? Array.from({length: 20}).map((_, i) => (
            <div key={i} className="h-40 rounded-xl bg-rh-dark border border-rh-gray animate-pulse p-5">
              <div className="h-6 w-1/3 bg-rh-gray/50 rounded mb-4"></div>
              <div className="h-4 w-2/3 bg-rh-gray/30 rounded mb-8"></div>
              <div className="h-8 w-1/2 bg-rh-gray/50 rounded"></div>
            </div>
          ))
          : stocks.map((stock) => (
            <StockCard key={stock.Symbol} stock={stock}/>
          ))
        }
      </div>
    </section>
  );
}
