"use client";

import { useState } from "react";
import MapView from "@/components/MapView";
import PredictionChart from "@/components/PredictionChart";

export default function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string; steps?: string[] }[]>([
    { role: "agent", content: "Hello! I am your TerraSight Orchestrator. How can I help you analyze Dubai real estate today?" }
  ]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState<string>("");

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = query;
    setQuery("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setIsAnalyzing(true);
    setCurrentStep("Initializing agents...");

    // We use fetch and read the stream instead of EventSource because EventSource only supports GET
    try {
      const response = await fetch("http://localhost:8000/agent-query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage, budget: 500000 })
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let finalAnswer = "";
      const steps: string[] = [];

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.replace('data: ', ''));
                if (data.status === "Done") {
                  finalAnswer = data.result.answer;
                  setCurrentStep("");
                } else {
                  setCurrentStep(data.status);
                  steps.push(data.status);
                }
              } catch (e) {
                console.error("SSE parse error", e);
              }
            }
          }
        }
      }

      setMessages(prev => [...prev, { role: "agent", content: finalAnswer, steps }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: "agent", content: "Sorry, an error occurred while analyzing the data." }]);
    } finally {
      setIsAnalyzing(false);
      setCurrentStep("");
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">TerraSight AI</h1>
            <p className="text-slate-400 mt-1">Dubai Real Estate Predictive Analytics</p>
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
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 h-[800px] flex flex-col">
              <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`p-3 rounded-lg w-[85%] ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-slate-800 text-slate-300 rounded-tl-none'}`}>
                      <p className="text-sm whitespace-pre-line">{msg.content}</p>
                      
                      {/* Subagent steps visualization */}
                      {msg.steps && msg.steps.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-700">
                          <p className="text-xs text-slate-400 mb-1 font-semibold">Agent Workflow:</p>
                          <ul className="text-xs text-slate-500 space-y-1">
                            {msg.steps.map((step, i) => (
                              <li key={i} className="flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                                {step}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {/* Streaming Analyzing State */}
                {isAnalyzing && (
                  <div className="flex flex-col items-start">
                    <div className="p-3 rounded-lg w-[85%] bg-slate-800 text-slate-300 rounded-tl-none border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                      <div className="flex items-center gap-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                        </div>
                        <p className="text-sm font-medium text-blue-400 animate-pulse">{currentStep}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-auto">
                <form onSubmit={handleQuery} className="flex gap-2">
                  <input 
                    type="text" 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g. I have 500k AED, JVC or Arjan?" 
                    disabled={isAnalyzing}
                    className="w-full bg-slate-800 border border-slate-700 rounded-md px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
                  />
                  <button type="submit" disabled={isAnalyzing} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium transition-colors disabled:opacity-50">
                    Send
                  </button>
                </form>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
