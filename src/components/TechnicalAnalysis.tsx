import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

interface TechnicalIndicators {
  trend_indicators: {
    moving_averages: {
      date: string;
      sma20: number;
      sma50: number;
      ema12: number;
      ema26: number;
    }[];
  };
}

export default function TechnicalAnalysis({ data }: { data: TechnicalIndicators }) {
  if (!data?.trend_indicators?.moving_averages) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-4">
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data.trend_indicators.moving_averages}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="sma20" stroke="#8884d8" name="SMA 20" />
            <Line type="monotone" dataKey="sma50" stroke="#82ca9d" name="SMA 50" />
            <Line type="monotone" dataKey="ema12" stroke="#ffc658" name="EMA 12" />
            <Line type="monotone" dataKey="ema26" stroke="#ff7300" name="EMA 26" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}