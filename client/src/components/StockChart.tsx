import {
  ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';

interface Props {
  data: any[];
  color: string;
}

export default function StockChart({data, color}: Props) {
  return (
    <div className="h-100 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data}>
          <defs>
            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
            <pattern id="predictionPattern" patternUnits="userSpaceOnUse" width="4" height="4">
              <path d="M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2" stroke={color} strokeWidth="1" opacity={0.2}/>
            </pattern>
          </defs>

          <XAxis dataKey="Date" hide={true}/>
          <YAxis domain={['auto', 'auto']} hide={true}/>

          <Tooltip
            contentStyle={{backgroundColor: '#1A1A1A', border: '1px solid #333', borderRadius: '8px'}}
            itemStyle={{color: '#fff'}}
            formatter={(value: any, name: any) => {
              if (name === "Close") return [`$${Number(value).toFixed(2)}`, "Price"];
              if (name === "PredictedClose") return [`$${Number(value).toFixed(2)}`, "AI Forecast"];
              if (name === "UpperBound") return [`$${Number(value).toFixed(2)}`, "Max Range"];
              if (name === "LowerBound") return [`$${Number(value).toFixed(2)}`, "Min Range"];
              return [`$${value}`, name];
            }}
            labelStyle={{color: '#888', marginBottom: '4px'}}
          />

          <Area
            type="monotone"
            dataKey="UpperBound"
            baseLine={0}
            stroke="none"
            fill={color}
            fillOpacity={0.05}
          />

          <Area
            type="monotone"
            dataKey="Close"
            stroke={color}
            strokeWidth={2}
            fill="url(#colorGradient)"
          />

          <Line
            type="monotone"
            dataKey="PredictedClose"
            stroke={color}
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{r: 2, fill: color}}
            activeDot={{r: 6}}
          />

          {data.find(d => d.PredictedClose) && (
            <ReferenceLine x={data.find(d => d.PredictedClose)?.Date} stroke="#555" strokeDasharray="3 3"
                           label={{position: 'top', value: 'AI Forecast', fill: '#888', fontSize: 12}}/>
          )}

        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
