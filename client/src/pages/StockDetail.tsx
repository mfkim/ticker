import {useEffect, useState, useMemo} from "react";
import {useParams, useNavigate} from "react-router-dom";
import StockChart from "../components/StockChart";
import type {StockDetailResponse} from "../types";

// 기간 필터 옵션
const TIME_RANGES = [
  {label: "1W", days: 7},
  {label: "1M", days: 30},
  {label: "3M", days: 90},
  {label: "1Y", days: 365},
];

export default function StockDetail() {
  const {symbol} = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState<StockDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedRange, setSelectedRange] = useState("1M"); // 기본값 1달

  useEffect(() => {
    fetch(`/api/v1/stocks/${symbol}`)
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [symbol]);

  // 기간 필터링 로직 (useMemo로 최적화)
  const filteredPrices = useMemo(() => {
    if (!data?.prices) return [];
    const days = TIME_RANGES.find(r => r.label === selectedRange)?.days || 365;
    // prices는 이미 최신순(DESC)으로 정렬되어 옴 -> 앞에서부터 자르면 최신 데이터
    return data.prices.slice(0, days);
  }, [data, selectedRange]);

  if (loading) return <div className="text-white text-center py-20 animate-pulse">Loading...</div>;
  if (!data || !data.prices || data.prices.length === 0) return <div className="text-white text-center py-20">No
    Data</div>;

  const info = data.info;
  const latest = data.prices[0];
  const closePrice = latest.Close ?? 0;
  const changeRate = latest.ChangeRate ?? 0;

  const isUp = changeRate >= 0;
  const colorHex = isUp ? "#00C805" : "#FF5000";
  const textColor = isUp ? "text-rh-green" : "text-rh-red";

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 text-white animate-fade-in">

      {/* 1. 네비게이션 */}
      <button onClick={() => navigate(-1)}
              className="text-rh-subtext hover:text-white text-sm font-bold mb-6 flex items-center gap-1 transition-colors cursor-pointer">
        ← Back
      </button>

      {/* 2. 헤더 (기업 정보 포함) */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-4xl font-black tracking-tight">{info.Symbol}</h1>
          <p className="text-lg font-bold mt-1">{info.Name}</p>
          {/* 섹터 & 산업 정보 배지 */}
          <div className="flex gap-2 mt-3">
            <span
              className="px-2 py-1 bg-rh-gray/30 rounded text-xs font-medium text-rh-subtext border border-rh-gray">{info.Sector || 'Sector N/A'}</span>
            <span
              className="px-2 py-1 bg-rh-gray/30 rounded text-xs font-medium text-rh-subtext border border-rh-gray">{info.Industry || 'Industry N/A'}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-4xl font-bold">${closePrice.toLocaleString()}</div>
          <div className={`text-xl font-bold ${textColor} mt-1`}>
            {isUp ? "+" : ""}{changeRate.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="h-px w-full bg-rh-gray my-6"></div>

      {/* 3. 차트 영역 */}
      <div className="relative">
        {filteredPrices.length > 0 && <StockChart data={filteredPrices} color={colorHex}/>}
      </div>

      {/* 4. 기간 선택 버튼 (Robinhood Style) */}
      <div className="flex gap-1 mt-6 border-b border-rh-gray pb-4">
        {TIME_RANGES.map((range) => (
          <button
            key={range.label}
            onClick={() => setSelectedRange(range.label)}
            className={`px-4 py-2 text-sm font-bold rounded-lg transition-all ${
              selectedRange === range.label
                ? "text-rh-green bg-rh-green/10"
                : "text-rh-subtext hover:text-white hover:bg-rh-gray/30"
            }`}
          >
            {range.label}
          </button>
        ))}
      </div>

      {/* 5. 키 스탯 */}
      <div className="mt-8">
        <h3 className="text-xl font-bold mb-6">Key Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-y-8 gap-x-4">
          <StatItem label="Market Cap" value={info.MarketCap ? `$${(info.MarketCap / 1e9).toFixed(2)}B` : "-"}/>
          <StatItem label="Volume" value={latest.Volume ? latest.Volume.toLocaleString() : "-"}/>
          <StatItem label="High (Today)" value={latest.High ? `$${latest.High.toLocaleString()}` : "-"}/>
          <StatItem label="Low (Today)" value={latest.Low ? `$${latest.Low.toLocaleString()}` : "-"}/>
          <StatItem label="Open" value={latest.Open ? `$${latest.Open.toLocaleString()}` : "-"}/>
          <StatItem label="RSI (14)" value={latest.RSI_14 ? latest.RSI_14.toFixed(1) : "-"}/>
        </div>
      </div>

    </div>
  );
}

function StatItem({label, value}: { label: string, value: string }) {
  return (
    <div>
      <div className="text-rh-subtext text-xs font-bold uppercase tracking-wider mb-1">{label}</div>
      <div className="text-white text-lg font-medium">{value}</div>
    </div>
  )
}
