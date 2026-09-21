"use client";

import { useState, useMemo } from "react";
import Map, { Source, Layer } from "react-map-gl/mapbox";
import type { HeatmapLayer } from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

const INITIAL_VIEW_STATE = {
  longitude: 55.2308,
  latitude: 25.0648,
  zoom: 12,
  pitch: 45,
  bearing: -17.6,
};

// No hardcoded coordinates needed! Backend sends lat/lng dynamically
const heatmapLayer: HeatmapLayer = {
  id: "appreciation-heatmap-layer",
  type: "heatmap",
  source: "dubai-points",
  paint: {
    "heatmap-weight": ["interpolate", ["linear"], ["get", "appreciation"], 0, 0, 1, 1],
    "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 11, 1, 15, 3],
    "heatmap-color": [
      "interpolate", ["linear"], ["heatmap-density"],
      0, "rgba(33, 102, 172, 0)",
      0.2, "rgb(103, 169, 207)",
      0.4, "rgb(209, 229, 240)",
      0.6, "rgb(253, 219, 199)",
      0.8, "rgb(239, 138, 98)",
      1, "rgb(178, 24, 43)"
    ],
    "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 11, 25, 15, 60],
    "heatmap-opacity": 0.8,
  },
};

export default function MapView({ 
  data, 
  mode = "appreciation", 
  onModeChange 
}: { 
  data?: any[], 
  mode?: "appreciation" | "buy" | "sell",
  onModeChange?: (mode: "appreciation" | "buy" | "sell") => void 
}) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  const geojsonData = useMemo(() => {
    // If no dynamic data, show empty or default state
    const features = data && data.length > 0 
      ? data.map(item => {
          const coords = [item.lng || 55.2308, item.lat || 25.0648];
          
          let weight = 0.5;
          if (mode === "appreciation") {
            weight = Math.min(Math.max((item.predictions?.["12_month_appreciation_pct"] || 0) / 20, 0.1), 1.0);
          } else if (mode === "buy") {
            weight = Math.min(Math.max((item.weekly_buy_volume || 0) / 300, 0.1), 1.0);
          } else if (mode === "sell") {
            weight = Math.min(Math.max((item.weekly_sell_volume || 0) / 300, 0.1), 1.0);
          }

          return {
            type: "Feature",
            properties: { name: item.location, weight: weight },
            geometry: { type: "Point", coordinates: coords },
          };
        })
      : [
          // Fallback static points if no ML data yet
          { type: "Feature", properties: { name: "JVC Center", weight: 0.8 }, geometry: { type: "Point", coordinates: [55.205, 25.065] } },
          { type: "Feature", properties: { name: "Arjan Center", weight: 0.4 }, geometry: { type: "Point", coordinates: [55.242, 25.055] } },
        ];

    return {
      type: "FeatureCollection",
      features
    };
  }, [data, mode]);

  // Adjust colors based on mode
  const colorScale = useMemo(() => {
    if (mode === "buy") {
      return [
        0, "rgba(33, 102, 172, 0)",
        0.2, "rgb(199, 233, 192)",
        0.4, "rgb(161, 217, 155)",
        0.6, "rgb(116, 196, 118)",
        0.8, "rgb(49, 163, 84)",
        1, "rgb(0, 109, 44)" // Green for buy
      ];
    } else if (mode === "sell") {
      return [
        0, "rgba(33, 102, 172, 0)",
        0.2, "rgb(252, 187, 161)",
        0.4, "rgb(252, 146, 114)",
        0.6, "rgb(251, 106, 74)",
        0.8, "rgb(222, 45, 38)",
        1, "rgb(165, 15, 21)" // Dark red for sell
      ];
    } else {
      return [
        0, "rgba(33, 102, 172, 0)",
        0.2, "rgb(103, 169, 207)",
        0.4, "rgb(209, 229, 240)",
        0.6, "rgb(253, 219, 199)",
        0.8, "rgb(239, 138, 98)",
        1, "rgb(178, 24, 43)" // Standard heatmap
      ];
    }
  }, [mode]);

  const dynamicHeatmapLayer: HeatmapLayer = {
    ...heatmapLayer,
    paint: {
      ...heatmapLayer.paint,
      "heatmap-color": ["interpolate", ["linear"], ["heatmap-density"], ...colorScale] as any,
      "heatmap-weight": ["interpolate", ["linear"], ["get", "weight"], 0, 0, 1, 1],
    }
  };

  return (
    <div className="w-full h-full min-h-[400px] bg-slate-900 rounded-xl overflow-hidden border border-slate-800 relative">
      <Map
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
      >
        <Source id="dubai-points" type="geojson" data={geojsonData as any}>
          <Layer {...dynamicHeatmapLayer} />
        </Source>
      </Map>
      
      {/* Layer Controls */}
      <div className="absolute top-4 right-4 bg-slate-900/90 p-1.5 rounded-lg border border-slate-700 backdrop-blur-md flex gap-1 shadow-xl">
        <button 
          onClick={() => onModeChange?.("appreciation")}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${mode === 'appreciation' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
        >
          Appreciation
        </button>
        <button 
          onClick={() => onModeChange?.("buy")}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${mode === 'buy' ? 'bg-emerald-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
        >
          Buy Volume
        </button>
        <button 
          onClick={() => onModeChange?.("sell")}
          className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${mode === 'sell' ? 'bg-red-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
        >
          Sell Volume
        </button>
      </div>

      <div className="absolute top-4 left-4 bg-slate-900/80 p-3 rounded-lg border border-slate-700 backdrop-blur-sm text-sm text-white shadow-xl pointer-events-none">
        <h3 className="font-semibold mb-2">
          {mode === "buy" ? "High Buy Demand" : mode === "sell" ? "High Sell Supply" : "Appreciation Density"}
        </h3>
        <div className="flex flex-col gap-1 w-32">
          <div 
            className="h-3 w-full rounded" 
            style={{ 
              background: mode === 'buy' 
                ? 'linear-gradient(to right, rgba(33,102,172,0), rgb(116,196,118), rgb(0,109,44))' 
                : mode === 'sell'
                ? 'linear-gradient(to right, rgba(33,102,172,0), rgb(251,106,74), rgb(165,15,21))'
                : 'linear-gradient(to right, rgba(33,102,172,0), rgb(253,219,199), rgb(178,24,43))'
            }}
          ></div>
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>
      </div>
    </div>
  );
}
