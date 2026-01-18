import type {StockRanking} from "../types";
import {useNavigate} from "react-router-dom";

interface Props {
  stock: StockRanking;
}

export default function StockCard({stock}: Props) {
  const navigate = useNavigate();

  const changeRate = stock.ChangeRate ?? 0;
  const isUp = changeRate >= 0;

  const textColor = isUp ? "text-rh-green" : "text-rh-red";
  const bgBadge = isUp ? "bg-rh-green/10" : "bg-rh-red/10";
  const arrow = isUp ? "▲" : "▼";

  const handleClick = () => {
    navigate(`/stock/${stock.Symbol}`, {state: {name: stock.Name}});
  };

  return (
    <div
      onClick={handleClick}
      className="group relative flex flex-col justify-between p-5 bg-rh-dark border border-rh-gray rounded-xl transition-all duration-300 hover:-translate-y-1 hover:border-rh-green/50 hover:shadow-lg hover:shadow-rh-green/10 cursor-pointer"
    >

      {/* 상단: 심볼 및 회사명 */}
      <div className="mb-4">
        <div className="flex justify-between items-start">
          <h3 className="text-xl font-black tracking-tight text-white group-hover:text-rh-green transition-colors">
            {stock.Symbol}
          </h3>
        </div>
        <p className="text-xs font-medium text-rh-subtext truncate mt-1" title={stock.Name}>
          {stock.Name}
        </p>
      </div>

      {/* 하단: 가격 및 등락률 */}
      <div className="flex items-end justify-between">
        <span className="text-2xl font-bold text-white tracking-tight">
          ${stock.Close.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
        </span>

        {/* 등락률 배지 */}
        <div className={`flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold ${textColor} ${bgBadge}`}>
          <span className="text-[10px]">{arrow}</span>
          <span>{Math.abs(changeRate).toFixed(2)}%</span>
        </div>
      </div>

    </div>
  );
}
