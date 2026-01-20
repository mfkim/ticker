import {useEffect, useState, useMemo} from "react";
import {useParams, useNavigate} from "react-router-dom";
import StockChart from "../components/StockChart";
import type {StockDetailResponse, PredictionData} from "../types";

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
  const [prediction, setPrediction] = useState<PredictionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [selectedRange, setSelectedRange] = useState("1M");

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

  const handlePredict = async () => {
    if (predicting) return;
    setPredicting(true);
    try {
      const res = await fetch(`/api/v1/stocks/${symbol}/predict?days=30`);
      if (!res.ok) throw new Error("Prediction failed");
      const result = await res.json();
      setPrediction(result);
    } catch (err) {
      console.error(err);
      alert("Failed to fetch prediction data.");
    } finally {
      setPredicting(false);
    }
  };

  const chartData = useMemo(() => {
    if (!data?.prices) return [];

    const days = TIME_RANGES.find(r => r.label === selectedRange)?.days || 365;
    const history = [...data.prices].slice(0, days).reverse();

    if (prediction.length > 0) {
      return [...history, ...prediction];
    }

    return history;
  }, [data, selectedRange, prediction]);

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

      <button onClick={() => navigate(-1)}
              className="text-rh-subtext hover:text-white text-sm font-bold mb-6 flex items-center gap-1 transition-colors cursor-pointer">
        ← Back
      </button>

      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-4xl font-black tracking-tight">{info.Symbol}</h1>
          <p className="text-lg font-bold mt-1">{info.Name}</p>
          <div className="flex gap-2 mt-3">
            <span
              className="px-2 py-1 bg-rh-gray/30 rounded text-xs font-medium text-rh-subtext border border-rh-gray">{info.Sector || 'N/A'}</span>
            <span
              className="px-2 py-1 bg-rh-gray/30 rounded text-xs font-medium text-rh-subtext border border-rh-gray">{info.Industry || 'N/A'}</span>
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

      <div className="relative">
        <StockChart data={chartData} color={colorHex}/>
      </div>

      <div className="flex flex-col md:flex-row justify-between items-center mt-6 border-b border-rh-gray pb-4 gap-4">
        <div className="flex gap-1">
          {TIME_RANGES.map((range) => (
            <button
              key={range.label}
              onClick={() => {
                setSelectedRange(range.label);
                setPrediction([]);
              }}
              className={`px-4 py-2 text-sm font-bold rounded-lg transition-all cursor-pointer ${
                selectedRange === range.label
                  ? "text-rh-green bg-rh-green/10"
                  : "text-rh-subtext hover:text-white hover:bg-rh-gray/30"
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>

        <button
          onClick={handlePredict}
          disabled={predicting || prediction.length > 0}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-full font-bold transition-all cursor-pointer ${
            prediction.length > 0
              ? "bg-rh-gray/20 text-rh-subtext cursor-default"
              : "bg-linear-to-r from-rh-green to-emerald-400 text-black hover:opacity-90 hover:scale-105 active:scale-95 shadow-lg shadow-rh-green/20"
          }`}
        >
          {predicting ? (
            <>
              <svg className="animate-spin h-4 w-4 text-black" xmlns="http://www.w3.org/2000/svg" fill="none"
                   viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing...
            </>
          ) : prediction.length > 0 ? (
            <>✅ Forecast Ready</>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                      d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              Run AI Forecast
            </>
          )}
        </button>
      </div>

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
