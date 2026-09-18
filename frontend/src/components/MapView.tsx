"use client";

import { useState } from "react";
import Map, { Source, Layer } from "react-map-gl/mapbox";
import type { HeatmapLayer } from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

// Dubai koordinatları
const INITIAL_VIEW_STATE = {
  longitude: 55.2308,
  latitude: 25.0648,
  zoom: 12, // Biraz daha yakınlaştık ki noktalar (heatmap) daha iyi görünsün
  pitch: 45,
  bearing: -17.6,
};

// Nokta tabanlı (Point) GeoJSON verisi (Yuvarlak/Smooth Heatmap için)
const geojsonData: any = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: { name: "JVC Center", appreciation: 0.8 }, // 0 ile 1 arası normalize edilmiş değerler (Heatmap weight için daha iyi)
      geometry: { type: "Point", coordinates: [55.205, 25.065] },
    },
    {
      type: "Feature",
      properties: { name: "JVC North", appreciation: 0.6 },
      geometry: { type: "Point", coordinates: [55.210, 25.075] },
    },
    {
      type: "Feature",
      properties: { name: "Arjan Center", appreciation: 0.4 },
      geometry: { type: "Point", coordinates: [55.242, 25.055] },
    },
    {
      type: "Feature",
      properties: { name: "Dubai Hills Estate", appreciation: 1.0 },
      geometry: { type: "Point", coordinates: [55.265, 25.100] },
    },
    {
      type: "Feature",
      properties: { name: "Motor City", appreciation: 0.5 },
      geometry: { type: "Point", coordinates: [55.235, 25.045] },
    },
  ],
};

// Yumuşak geçişli (Smooth) Heatmap katmanı ayarları
const heatmapLayer: HeatmapLayer = {
  id: "appreciation-heatmap-layer",
  type: "heatmap",
  source: "dubai-points",
  paint: {
    // Verideki 'appreciation' değerine göre yoğunluğu (ağırlığı) artır
    "heatmap-weight": [
      "interpolate",
      ["linear"],
      ["get", "appreciation"],
      0, 0,
      1, 1
    ],
    // Zoom seviyesine göre genel parlaklık/yoğunluk
    "heatmap-intensity": [
      "interpolate",
      ["linear"],
      ["zoom"],
      11, 1,
      15, 3
    ],
    // Heatmap'in renk skalası (Düşükten yükseğe)
    "heatmap-color": [
      "interpolate",
      ["linear"],
      ["heatmap-density"],
      0, "rgba(33, 102, 172, 0)", // Şeffaf
      0.2, "rgb(103, 169, 207)",  // Mavi
      0.4, "rgb(209, 229, 240)",  // Açık mavi
      0.6, "rgb(253, 219, 199)",  // Açık turuncu
      0.8, "rgb(239, 138, 98)",   // Turuncu
      1, "rgb(178, 24, 43)"       // Kırmızı (En çok değerlenen yerler)
    ],
    // Noktaların yayılma yarıçapı (Zoom yaptıkça büyür)
    "heatmap-radius": [
      "interpolate",
      ["linear"],
      ["zoom"],
      11, 25,
      15, 60
    ],
    // Genel şeffaflık
    "heatmap-opacity": 0.8,
  },
};

export default function MapView() {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  return (
    <div className="w-full h-full min-h-[400px] bg-slate-900 rounded-xl overflow-hidden border border-slate-800 relative">
      <Map
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
      >
        <Source id="dubai-points" type="geojson" data={geojsonData}>
          <Layer {...heatmapLayer} />
        </Source>
      </Map>
      
      {/* Harita Üzeri Bilgi Kutucuğu (Legend) */}
      <div className="absolute top-4 left-4 bg-slate-900/80 p-3 rounded-lg border border-slate-700 backdrop-blur-sm text-sm text-white">
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
