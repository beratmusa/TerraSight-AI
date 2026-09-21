"use client";

import { useMemo } from "react";
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

const COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6"];

export default function PredictionChart({ data }: { data?: any[] }) {
  
  const chartData = useMemo(() => {
    // If no data, return default mock
    if (!data || data.length === 0) {
      return [
        { year: "2024", JVC: 450000, Arjan: 480000 },
        { year: "2025", JVC: 480000, Arjan: 500000 },
        { year: "2026", JVC: 520000, Arjan: 535000 },
        { year: "2027", JVC: 575000, Arjan: 580000 },
        { year: "2028", JVC: 640000, Arjan: 630000 },
      ];
    }

    // Generate 5-year compound growth using the ML prediction percentage
    const currentYear = new Date().getFullYear();
    const baseValue = 500000; // Starting budget/value

    return Array.from({ length: 5 }).map((_, i) => {
      const yearStr = (currentYear + i).toString();
      const yearObj: any = { year: yearStr };
      
      data.forEach(item => {
        const pct = (item.predictions?.["12_month_appreciation_pct"] || 5) / 100;
        // Compound interest formula: A = P(1 + r)^t
        yearObj[item.location] = Math.round(baseValue * Math.pow(1 + pct, i));
      });
      
      return yearObj;
    });
  }, [data]);

  // Extract unique locations from data for lines
  const locations = data && data.length > 0 ? data.map(d => d.location) : ["JVC", "Arjan"];

  return (
    <div className="w-full h-[300px] bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-blue-500/5 blur-[60px] rounded-full pointer-events-none"></div>
      
      <h3 className="text-sm font-semibold text-slate-300 mb-4 tracking-wide uppercase">5-Year Growth Trajectory (AED)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} opacity={0.5} />
          <XAxis 
            dataKey="year" 
            stroke="#64748b" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false} 
            dy={10}
          />
          <YAxis 
            stroke="#64748b" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false} 
            tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
            dx={-10}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "12px", boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.5)" }}
            itemStyle={{ fontSize: "14px", fontWeight: "500" }}
            labelStyle={{ color: "#94a3b8", marginBottom: "4px" }}
            formatter={(value: number) => [`${value.toLocaleString()} AED`, undefined]}
          />
          <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
          
          {locations.map((loc, i) => (
            <Line 
              key={loc}
              type="monotone" 
              dataKey={loc} 
              stroke={COLORS[i % COLORS.length]} 
              strokeWidth={3} 
              dot={{ r: 4, fill: COLORS[i % COLORS.length], strokeWidth: 2, stroke: "#0f172a" }} 
              activeDot={{ r: 7, strokeWidth: 0 }} 
              animationDuration={1500}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
