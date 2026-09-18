"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

const data = [
  { year: "2024", JVC: 450000, Arjan: 480000, DubaiHills: 1200000 },
  { year: "2025", JVC: 480000, Arjan: 500000, DubaiHills: 1250000 },
  { year: "2026", JVC: 520000, Arjan: 535000, DubaiHills: 1320000 },
  { year: "2027", JVC: 575000, Arjan: 580000, DubaiHills: 1400000 },
  { year: "2028", JVC: 640000, Arjan: 630000, DubaiHills: 1510000 },
];

export default function PredictionChart() {
  return (
    <div className="w-full h-[300px] bg-slate-900 border border-slate-800 rounded-xl p-4">
      <h3 className="text-sm font-medium text-slate-400 mb-4">5-Year Price Predictions (AED)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis 
            dataKey="year" 
            stroke="#94a3b8" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false} 
          />
          <YAxis 
            stroke="#94a3b8" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false} 
            tickFormatter={(value) => `${value / 1000}k`}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "8px" }}
            itemStyle={{ fontSize: "14px" }}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} />
          <Line 
            type="monotone" 
            dataKey="JVC" 
            stroke="#10b981" 
            strokeWidth={3} 
            dot={{ r: 4, fill: "#10b981" }} 
            activeDot={{ r: 6 }} 
          />
          <Line 
            type="monotone" 
            dataKey="Arjan" 
            stroke="#3b82f6" 
            strokeWidth={3} 
            dot={{ r: 4, fill: "#3b82f6" }} 
          />
          <Line 
            type="monotone" 
            dataKey="DubaiHills" 
            stroke="#f59e0b" 
            strokeWidth={3} 
            dot={{ r: 4, fill: "#f59e0b" }} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
