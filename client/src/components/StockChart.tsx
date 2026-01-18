import {AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer} from 'recharts';

interface StockData {
  Date: string;
  Close: number;
}

interface Props {
  data: StockData[];
  color: string;
}

export default function StockChart({data, color}: Props) {
  // 데이터 순서가 최신순이면 뒤집어줘야 함 (차트는 과거->현재 순)
  const chartData = [...data].reverse();

  return (
    <div className="h-[400px] w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>

          <XAxis
            dataKey="Date"
            hide={true} // X축 날짜 숨김 (심플함 추구)
          />
          <YAxis
            domain={['auto', 'auto']} // 값의 범위에 맞춰 차트 높이 자동 조절
            hide={true} // Y축 가격 숨김
          />

          <Tooltip
            contentStyle={{backgroundColor: '#1A1A1A', border: '1px solid #333', borderRadius: '8px'}}
            itemStyle={{color: '#fff'}}
            labelStyle={{color: '#888', marginBottom: '4px'}}
            formatter={(value: any) => [`$${value.toFixed(2)}`, 'Price']}
          />

          <Area
            type="monotone"
            dataKey="Close"
            stroke={color}
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
