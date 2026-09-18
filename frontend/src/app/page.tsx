import MapView from "@/components/MapView";
import PredictionChart from "@/components/PredictionChart";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">TerraSight AI</h1>
            <p className="text-slate-400 mt-1">Dubai Real Estate Predictive Analytics</p>
          </div>
          <div className="flex gap-4">
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors">
              New Query
            </button>
          </div>
        </header>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 flex flex-col gap-8">
            <div className="space-y-4 h-[400px]">
              <h2 className="text-xl font-semibold">AI Prediction Heatmap</h2>
              <MapView />
            </div>
            
            <div className="space-y-4 pt-10">
              <h2 className="text-xl font-semibold">Growth Trends</h2>
              <PredictionChart />
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">AI Orchestrator</h2>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 h-[500px] flex flex-col">
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                <div className="bg-slate-800 p-3 rounded-lg rounded-tl-none w-[85%]">
                  <p className="text-sm text-slate-300">Hello! I am your TerraSight Orchestrator. How can I help you analyze Dubai real estate today?</p>
                </div>
              </div>
              <div className="mt-auto">
                <input 
                  type="text" 
                  placeholder="e.g. I have 500k AED, JVC or Arjan?" 
                  className="w-full bg-slate-800 border border-slate-700 rounded-md px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
