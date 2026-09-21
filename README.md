# TerraSight AI 🏙️🤖

> **Predictive Analytics & Multi-Agent AI System for the Dubai Real Estate Market**

TerraSight AI is an enterprise-grade MVP designed to help investors make data-driven decisions in the fast-paced Dubai real estate market. It combines interactive mapping, advanced machine learning (CatBoost), and a multi-agent LLM architecture (powered by Google Gemini) to provide tailored investment strategies.

## 🌟 Key Features

- **🗺️ Interactive AI Heatmaps:** Visualizes neighborhood appreciation potential using smooth, data-driven Mapbox GL JS heatmaps.
- **📈 12-Month Predictive Analytics (CatBoost):** Forecasts 12-month capital appreciation using 16+ complex features including:
  - *GIS Metrics:* Distance to beach, drive time to Burj Khalifa, amenity density.
  - *Financial Metrics:* Regional momentum, ROI (rental yield), supply pressure, days on market.
  - *Property Specs:* Developer tier, project stage (off-plan vs ready), service charges.
- **🤖 Multi-Agent Orchestration (Gemini 3.6 Flash):** An intelligent Orchestrator Agent that delegates tasks to:
  - *Data Retrieval Agent:* Fetches historical prices and geospatial metrics.
  - *ML Prediction Agent:* Runs CatBoost inference.
  - *RAG Context Agent:* Provides context from Dubai 2040 Urban Master Plan and real estate news.
- **✨ Visual Feast UI:** A stunning, animated Chat UI built with Framer Motion, React Markdown, Recharts, and Tailwind CSS.

## 🏗️ Automated Pipelines (MLOps & Data Eng)

TerraSight AI includes built-in cron-ready pipelines to ensure the AI never relies on stale data:
- **`ml_pipeline.py` (Incremental Learning):** Simulates fetching daily transactions from Dubai Pulse and GIS data from OSM. Uses CatBoost's **Warm Start** (`init_model`) to incrementally train the model on new data in seconds without starting from scratch.
- **`rag_pipeline.py`:** Simulates scraping real estate news (Zawya, Gulf News) and official PDFs, generating embeddings, and upserting them into Supabase `pgvector`.

## 🛠️ Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS, shadcn/ui, Framer Motion
- **Maps & Charts:** Mapbox GL JS (`react-map-gl`), Recharts
- **Markdown:** `react-markdown`, `remark-gfm`

### Backend
- **Framework:** Python (FastAPI)
- **AI / Agents:** LangChain / LangGraph, Google Gemini (`gemini-3.6-flash`)
- **Machine Learning:** CatBoost (`.cbm`), pandas
- **Database Architecture:** Supabase (PostgreSQL, pgvector), TimescaleDB
- **Infrastructure:** Docker & Docker Compose

## 🚀 Quick Start

### 1. Prerequisites
- Node.js (v18+)
- Python (3.11+)
- Mapbox Access Token
- Google Gemini API Key

### 2. Frontend Setup
```bash
cd frontend
npm install

# Create a .env.local file and add your Mapbox token
echo "NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here" > .env.local

npm run dev
```
*Frontend will be available at http://localhost:3000*

### 3. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create a .env file and add your Gemini API token
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env

# Generate the initial CatBoost model
python create_model.py

# Run FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend API docs will be available at http://localhost:8000/docs*

---
*Built for the future of Dubai Real Estate.*
