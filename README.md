# TerraSight AI 🏙️🤖

> **Predictive Analytics & Multi-Agent AI System for the Dubai Real Estate Market**

TerraSight AI is an intelligent MVP designed to help investors make data-driven decisions in the fast-paced Dubai real estate market. It combines interactive mapping, machine learning predictions, and a multi-agent LLM architecture to provide personalized insights.

## 🌟 Features

- **🗺️ Interactive AI Heatmaps:** Visualizes neighborhood appreciation potential (e.g., JVC, Arjan, Dubai Hills) using smooth, data-driven Mapbox GL JS heatmaps.
- **📈 5-Year ROI Predictions:** Utilizes Machine Learning (scikit-learn/XGBoost) to forecast property values over 1 to 5 years.
- **🤖 Multi-Agent Orchestration:** Powered by an intelligent Orchestrator Agent that delegates tasks to:
  - *Data Retrieval Agent:* Fetches historical prices and geospatial metrics from Supabase/TimescaleDB.
  - *ML Prediction Agent:* Runs predictive models on specific districts.
  - *RAG Context Agent:* Analyzes Dubai 2040 Urban Master Plan and real estate regulations using `pgvector`.
- **📊 Modern Dashboard:** Built with Next.js 14, Tailwind CSS, Recharts, and shadcn/ui.

## 🛠️ Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS & shadcn/ui
- **Maps:** Mapbox GL JS (`react-map-gl`)
- **Charts:** Recharts

### Backend
- **Framework:** Python (FastAPI)
- **AI / Agents:** LangGraph / LangChain, OpenAI
- **Machine Learning:** scikit-learn, pandas, XGBoost
- **Database:** Supabase (PostgreSQL, pgvector), TimescaleDB
- **Infrastructure:** Docker & Docker Compose

## 🚀 Quick Start

### 1. Prerequisites
- Node.js (v18+)
- Python (3.11+)
- Mapbox Access Token (Free)
- OpenAI API Key (For the AI Orchestrator)

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

# Run FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend API docs will be available at http://localhost:8000/docs*

### 4. Running with Docker (Optional)
You can spin up both frontend and backend using Docker Compose:
```bash
docker-compose up --build
```

---
*Built for the future of Dubai Real Estate.*
