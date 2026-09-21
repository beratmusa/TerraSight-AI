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

export default function MapView({ data }: { data?: any[] }) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  const geojsonData = useMemo(() => {
    // If no dynamic data, show empty or default state
    const features = data && data.length > 0 
      ? data.map(item => {
          const coords = [item.lng || 55.2308, item.lat || 25.0648];
          // Normalize appreciation (e.g. 15% -> 0.8 weight)
          const weight = Math.min(Math.max((item.predictions?.["12_month_appreciation_pct"] || 0) / 20, 0.1), 1.0);
          return {
            type: "Feature",
            properties: { name: item.location, appreciation: weight },
            geometry: { type: "Point", coordinates: coords },
          };
        })
      : [
          // Fallback static points if no ML data yet
          { type: "Feature", properties: { name: "JVC Center", appreciation: 0.8 }, geometry: { type: "Point", coordinates: [55.205, 25.065] } },
          { type: "Feature", properties: { name: "Arjan Center", appreciation: 0.4 }, geometry: { type: "Point", coordinates: [55.242, 25.055] } },
        ];

    return {
      type: "FeatureCollection",
      features
    };
  }, [data]);

  return (
    <div className="w-full h-full min-h-[400px] bg-slate-900 rounded-xl overflow-hidden border border-slate-800 relative">
      <Map
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
      >
        <Source id="dubai-points" type="geojson" data={geojsonData as any}>
          <Layer {...heatmapLayer} />
        </Source>
      </Map>
      
      <div className="absolute top-4 left-4 bg-slate-900/80 p-3 rounded-lg border border-slate-700 backdrop-blur-sm text-sm text-white shadow-xl">
        <h3 className="font-semibold mb-2">Appreciation Density</h3>
        <div className="flex flex-col gap-1 w-32">
          <div className="h-3 w-full rounded bg-gradient-to-r from-[rgba(33,102,172,0)] via-[rgb(253,219,199)] to-[rgb(178,24,43)]"></div>
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>
      </div>
    </div>
  );
}
