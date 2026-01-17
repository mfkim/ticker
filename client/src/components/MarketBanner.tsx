import {useEffect, useState} from "react";
import type {StockRanking} from "../types";

export default function MarketBanner() {
  const [indices, setIndices] = useState<StockRanking[]>([]);

  useEffect(() => {
    // 백엔드에서 만든 3대 지수 API 호출
    fetch("/api/v1/indices/major")
      .then((res) => res.json())
      .then((data) => setIndices(data))
      .catch((err) => console.error("Index fetch error:", err));
  }, []);

  // 데이터가 없으면(로딩 중 or 에러) 아무것도 표시하지 않음
  if (indices.length === 0) return null;

  return (
    <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
      {indices.map((idx) => {
        const changeRate = idx.ChangeRate ?? 0;
        const isUp = changeRate >= 0;

        // 색상 설정 (상승: 초록, 하락: 빨강)
        const color = isUp ? "text-rh-green" : "text-rh-red";
        const bgBadge = isUp ? "bg-rh-green/10" : "bg-rh-red/10";
        const arrow = isUp ? "▲" : "▼";

        // 지수 심볼에서 '^' 제거하고 이름 매핑
        const displayName = idx.Name.replace("Dow Jones Industrial Average", "Dow Jones 30")
          .replace("NASDAQ Composite", "NASDAQ");

        return (
          <div
            key={idx.Symbol}
            className="relative overflow-hidden p-6 rounded-2xl bg-rh-dark border border-rh-gray shadow-lg group hover:-translate-y-1 transition-transform duration-300"
          >
            {/* 배경 데코레이션 (은은한 빛 효과) */}
            <div
              className={`absolute -top-10 -right-10 w-32 h-32 ${isUp ? 'bg-rh-green' : 'bg-rh-red'}/5 rounded-full blur-2xl transition-colors`}></div>

            <div className="relative z-10 flex flex-col justify-between h-full">
              {/* 지수 이름 */}
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-rh-subtext font-bold text-sm uppercase tracking-wider">
                  {displayName}
                </h3>
                <span className="text-xs font-mono text-rh-gray px-2 py-0.5 rounded border border-rh-gray/30">
                    {idx.Symbol.replace('^', '')}
                 </span>
              </div>

              {/* 가격 및 등락률 */}
              <div className="flex items-end justify-between">
                <span className="text-3xl font-black text-white tracking-tight">
                  {idx.Close.toLocaleString(undefined, {maximumFractionDigits: 2})}
                </span>

                <div
                  className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-sm font-bold ${color} ${bgBadge}`}>
                  <span>{arrow}</span>
                  <span>{Math.abs(changeRate).toFixed(2)}%</span>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
