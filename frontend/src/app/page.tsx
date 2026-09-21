"use client";

import { useState } from "react";
import MapView from "@/components/MapView";
import PredictionChart from "@/components/PredictionChart";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion, AnimatePresence } from "framer-motion";

export default function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string; steps?: string[] }[]>([
    { role: "agent", content: "Hello! I am your TerraSight Orchestrator. How can I help you analyze Dubai real estate today?" }
  ]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState<string>("");
  const [predictionData, setPredictionData] = useState<any[]>([]);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = query;
    setQuery("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setIsAnalyzing(true);
    setCurrentStep("Initializing agents...");

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
                  if (data.result.prediction_data) {
                    setPredictionData(data.result.prediction_data);
                  }
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

  // Custom Markdown Components for a visual feast
  const MarkdownComponents: any = {
    h3: ({ node, ...props }: any) => <h3 className="text-lg font-bold text-blue-400 mt-5 mb-3 tracking-tight" {...props} />,
    h4: ({ node, ...props }: any) => <h4 className="text-md font-bold text-slate-200 mt-4 mb-2" {...props} />,
    p: ({ node, ...props }: any) => <p className="mb-3 text-sm leading-relaxed text-slate-300" {...props} />,
    ul: ({ node, ...props }: any) => <ul className="list-disc pl-5 mb-4 space-y-1 text-sm text-slate-300" {...props} />,
    li: ({ node, ...props }: any) => <li className="pl-1" {...props} />,
    strong: ({ node, ...props }: any) => <strong className="text-white font-semibold bg-blue-900/20 px-1 rounded" {...props} />,
    table: ({ node, ...props }: any) => (
      <div className="overflow-x-auto my-5 rounded-lg border border-slate-700 shadow-xl">
        <table className="w-full text-sm text-left text-slate-300" {...props} />
      </div>
    ),
    thead: ({ node, ...props }: any) => <thead className="bg-slate-800/80 text-blue-300 text-xs uppercase tracking-wider" {...props} />,
    th: ({ node, ...props }: any) => <th className="px-4 py-3 font-semibold border-b border-slate-700" {...props} />,
    td: ({ node, ...props }: any) => <td className="px-4 py-3 border-b border-slate-700/50 bg-slate-800/30" {...props} />,
    hr: ({ node, ...props }: any) => <hr className="my-6 border-slate-700/60" {...props} />,
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
              <MapView data={predictionData} />
            </div>
            
            <div className="space-y-4 pt-10">
              <h2 className="text-xl font-semibold">Growth Trends</h2>
              <PredictionChart data={predictionData} />
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">AI Orchestrator</h2>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 h-[800px] flex flex-col shadow-2xl relative overflow-hidden">
              {/* Background Glow */}
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-32 bg-blue-600/10 blur-[80px] pointer-events-none rounded-full"></div>
              
              <div className="flex-1 overflow-y-auto space-y-5 mb-4 pr-2 relative z-10 custom-scrollbar">
                <AnimatePresence initial={false}>
                  {messages.map((msg, idx) => (
                    <motion.div 
                      key={idx}
                      initial={{ opacity: 0, y: 15, scale: 0.98 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      transition={{ duration: 0.4, ease: "easeOut" }}
                      className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                    >
                      <div 
                        className={`p-4 rounded-2xl w-[95%] shadow-sm ${
                          msg.role === 'user' 
                            ? 'bg-blue-600 text-white rounded-tr-sm' 
                            : 'bg-slate-800/80 border border-slate-700/50 text-slate-300 rounded-tl-sm'
                        }`}
                      >
                        {msg.role === 'user' ? (
                          <p className="text-sm whitespace-pre-line">{msg.content}</p>
                        ) : (
                          <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>
                            {msg.content}
                          </ReactMarkdown>
                        )}
                        
                        {/* Subagent steps visualization */}
                        {msg.steps && msg.steps.length > 0 && (
                          <div className="mt-5 pt-4 border-t border-slate-700/50">
                            <p className="text-[11px] uppercase tracking-wider text-slate-400 mb-2 font-bold">Agent Workflow</p>
                            <ul className="text-xs text-slate-500 space-y-1.5 font-mono">
                              {msg.steps.map((step, i) => (
                                <motion.li 
                                  initial={{ opacity: 0, x: -10 }}
                                  animate={{ opacity: 1, x: 0 }}
                                  transition={{ delay: i * 0.1 }}
                                  key={i} 
                                  className="flex items-center gap-2"
                                >
                                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></span>
                                  {step}
                                </motion.li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                {/* Streaming Analyzing State */}
                <AnimatePresence>
                  {isAnalyzing && (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="flex flex-col items-start"
                    >
                      <div className="p-3 rounded-2xl w-[95%] bg-slate-800/80 text-slate-300 rounded-tl-sm border border-blue-500/30 shadow-[0_0_20px_rgba(59,130,246,0.15)] relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/10 to-transparent -translate-x-full animate-[shimmer_2s_infinite]"></div>
                        <div className="flex items-center gap-3 relative z-10">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                          </div>
                          <p className="text-sm font-medium text-blue-400">{currentStep}</p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <div className="mt-auto relative z-10 pt-4 border-t border-slate-800">
                <form onSubmit={handleQuery} className="flex gap-2">
                  <input 
                    type="text" 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g. I have 500k AED, JVC or Arjan?" 
                    disabled={isAnalyzing}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50 transition-all shadow-inner"
                  />
                  <button type="submit" disabled={isAnalyzing} className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50 shadow-[0_0_15px_rgba(37,99,235,0.4)]">
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
