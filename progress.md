# TerraSight AI - Project Progress & Context 🚀

This document serves as the "memory" of the project. It tracks what has been built, the architectural decisions made, and the next steps. **AI Agents should read this file first** when resuming context.

## 🏗️ Architecture Overview
TerraSight AI is a Predictive Real Estate MVP for Dubai, utilizing an agentic AI workflow to combine Machine Learning (CatBoost) and NLP (RAG via Gemini) to provide investment advice.

- **Frontend:** Next.js 14, Tailwind CSS, shadcn/ui, Mapbox (Heatmaps), Recharts (Graphs).
- **Backend:** FastAPI, Python 3.13.
- **LLM Engine:** Google Gemini 2.5 Flash (via `langchain-google-genai`).
- **ML Engine:** CatBoost (predicting 12-month appreciation %).
- **Data Engineering:** Automated pipelines (Cron jobs) simulating fetches from Dubai Pulse (Sales) and OpenStreetMap (GIS distances).

## ✅ What Has Been Completed
1. **Monorepo Setup:** Frontend and Backend connected. CORS configured.
2. **Dashboard UI:** Mapbox GL JS integrated with a sleek heatmap layer. Recharts implemented for 5-year trend visualization. All UI is translated to English.
3. **Streaming AI Chatbot (SSE):** The frontend listens to server-sent events (`/agent-query`), showing a real-time "Analyzing..." progress state while background agents work.
4. **MLOps Pipeline (`ml_pipeline.py`):** 
   - Switched from scikit-learn/XGBoost to CatBoost.
   - Target variable changed to `12_month_appreciation_pct`.
   - Complex 16-feature dataset created (GIS data, ROI, Momentum, Days on Market).
   - "Warm Start" (Incremental Learning) implemented to train CatBoost on new data without starting from scratch. Model saved as `.cbm`.
5. **RAG Pipeline (`rag_pipeline.py`):** Boilerplate created for scraping Dubai 2040 Master plan PDFs and News (Zawya/Gulf News) for Supabase `pgvector` embeddings.
6. **LLM Switch (OpenAI -> Gemini):** Removed OpenAI dependencies. Replaced orchestrator logic with `langchain-google-genai`.
7. **Gemini Live Integration:** Connected the real `GEMINI_API_KEY`. The Orchestrator now uses `ChatGoogleGenerativeAI(model="gemini-2.5-flash")` to dynamically synthesize the ML predictions and RAG context into a tailored investment thesis!

## ⏳ What Is Currently Mocked
1. **Database / RAG Store:** Supabase (`pgvector` / `TimescaleDB`) is not yet connected. The RAG context returns a hardcoded dictionary.
2. **Data Fetching:** Dubai Pulse and OSM data fetches are simulated via local `transactions.csv` and Python arrays.
3. **Frontend Visuals:** Mapbox heatmap points and Rechart graph data are still static arrays in the frontend components, rather than fetching the live ML predictions.

## 🎯 Next Steps
- [ ] Connect Supabase PostgreSQL and set up the `pgvector` table for RAG.
- [ ] Make the Frontend Mapbox and Recharts components fetch data dynamically from the Backend instead of using static mock data.
- [ ] Implement actual Web Scraping (BeautifulSoup/Selenium) and OSM distance calculations in the data pipelines.
