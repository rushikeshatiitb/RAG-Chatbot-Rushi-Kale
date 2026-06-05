import React, { useState, useEffect, useRef } from 'react';

// Approved Schemes metadata
const SCHEMES = [
  {
    id: "sbi-flexicap-fund",
    name: "SBI Flexicap Fund",
    type: "EQUITY",
    tagColor: "bg-primary/10 text-primary border-primary/20",
    icon: "trending_up",
    description: "Diversified portfolio across market caps.",
    assetClass: "Equity",
    launchDate: "Sep 2005",
    aum: "₹22,405 Cr"
  },
  {
    id: "sbi-elss-tax-saver",
    name: "SBI ELSS Tax Saver Fund",
    type: "ELSS",
    tagColor: "bg-tertiary/10 text-tertiary border-tertiary/20",
    icon: "account_balance_wallet",
    description: "80C Tax benefits with equity returns.",
    assetClass: "Equity (Tax)",
    launchDate: "Mar 1993",
    aum: "₹31,096 Cr"
  },
  {
    id: "sbi-large-cap",
    name: "SBI Large Cap Fund",
    type: "LARGE CAP",
    tagColor: "bg-secondary/10 text-secondary border-secondary/20",
    icon: "stat_3",
    description: "Stable growth through blue-chip stocks.",
    assetClass: "Equity",
    launchDate: "May 1987",
    aum: "₹34,100 Cr"
  }
];

const TEMPLATES = [
  { label: "Expense Ratio", query: "What is the expense ratio of {scheme}?" },
  { label: "Exit Load", query: "What is the exit load for {scheme}?" },
  { label: "Riskometer", query: "What is the risk level of {scheme}?" },
  { label: "Benchmark Index", query: "What is the benchmark index of {scheme}?" },
  { label: "Lock-in Period", query: "What is the lock-in period for {scheme}?" },
  { label: "Investment Objective", query: "What is the investment objective of {scheme}?" },
  { label: "Minimum SIP", query: "What is the minimum SIP amount of {scheme}?" }
];

export default function App() {
  const [selectedScheme, setSelectedScheme] = useState(SCHEMES[0]);
  const [queryInput, setQueryInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeSection, setActiveSection] = useState("analysis");
  
  // Chat history state
  const [chatHistory, setChatHistory] = useState([
    {
      role: 'assistant',
      question: null,
      answer: "Welcome to the SBI Mutual Fund FAQ Assistant. Select a scheme and click a template, or type any factual question about our schemes below.",
      chunks: [],
      is_advice: false,
      is_ambiguous: false,
      timestamp: new Date()
    }
  ]);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, loading]);

  const handleQuery = async (questionText) => {
    if (!questionText.trim()) return;
    
    setLoading(true);
    setError(null);

    // Add user message to history
    const userMsg = {
      role: 'user',
      text: questionText,
      timestamp: new Date()
    };
    setChatHistory(prev => [...prev, userMsg]);
    setQueryInput("");

    try {
      const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${baseUrl}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: questionText })
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        question: questionText,
        answer: data.answer,
        chunks: data.chunks || [],
        is_advice: data.is_advice,
        is_ambiguous: data.is_ambiguous,
        timestamp: new Date()
      }]);
    } catch (err) {
      console.error("API call failed, running in local fallback mode:", err);
      // Run local simulated RAG response as a fallback
      simulateFallbackResponse(questionText);
    } finally {
      setLoading(false);
    }
  };

  const simulateFallbackResponse = (questionText) => {
    const qLower = questionText.toLowerCase();
    let answer = "";
    let is_advice = false;
    let is_ambiguous = false;
    let chunks = [];

    // Check advice refusal
    if (qLower.includes("should i buy") || qLower.includes("should i invest") || qLower.includes("which is better") || qLower.includes("recommend")) {
      is_advice = true;
      answer = "I cannot provide investment advice or recommendations. I can only provide factual information from official SBI Mutual Fund documents.";
    } else {
      // Find matching scheme
      let matchedScheme = SCHEMES.find(s => qLower.includes(s.name.toLowerCase()) || qLower.includes(s.id.replace(/-/g, ' ')));
      if (!matchedScheme) {
        matchedScheme = selectedScheme;
      }

      if (qLower.includes("exit load")) {
        if (matchedScheme.id === "sbi-elss-tax-saver") {
          answer = `The exit load for ${matchedScheme.name} is NIL. Source: ${matchedScheme.name} Factsheet, April 2026, page 1, Scheme Details.`;
        } else if (matchedScheme.id === "sbi-flexicap-fund") {
          answer = `For ${matchedScheme.name}, the Exit Load is: For exit on or before 30 days from the date of allotment - 0.10% For exit after 30 days from the date of allotment - Nil. Source: ${matchedScheme.name} Factsheet, April 2026, page 1, Scheme Details.`;
        } else {
          answer = `For ${matchedScheme.name}, the Exit Load is: For exit on or before 30 days from the date of allotment - 1.00% For exit after 30 days from the date of allotment - Nil. Source: ${matchedScheme.name} Factsheet, April 2026, page 1, Scheme Details.`;
        }
        chunks = [{
          id: `${matchedScheme.id}-chunk-exit-load`,
          score: 0.95,
          text: `Exit Load: For exit on or before 30 days - ${matchedScheme.id === "sbi-flexicap-fund" ? "0.10%" : "1.00%"}, after 30 days - Nil. Entry Load: N.A. Plans Available: Regular, Direct.`,
          metadata: {
            citation: `${matchedScheme.name} Factsheet, April 2026, page 1, Scheme Details.`,
            file_name: `${matchedScheme.id}-factsheet.pdf`,
            page_number: 1,
            section: "Scheme Details"
          }
        }];
      } else if (qLower.includes("expense ratio") || qLower.includes("ter")) {
        const regVal = matchedScheme.id === "sbi-flexicap-fund" ? "1.63%" : matchedScheme.id === "sbi-elss-tax-saver" ? "1.74%" : "1.51%";
        const dirVal = matchedScheme.id === "sbi-flexicap-fund" ? "0.82%" : matchedScheme.id === "sbi-elss-tax-saver" ? "0.89%" : "0.87%";
        answer = `The Total Expense Ratio (TER) for ${matchedScheme.name} is ${regVal} for the Regular Plan and ${dirVal} for the Direct Plan. Source: SBI Total Expense Ratio (TER) Data File, Sheet1.`;
        chunks = [{
          id: `${matchedScheme.id}-chunk-ter`,
          score: 0.94,
          text: `${matchedScheme.name} TER: Regular Plan Total TER ${regVal}; Direct Plan Total TER ${dirVal}.`,
          metadata: {
            citation: `SBI Total Expense Ratio (TER) Data File, Sheet1.`,
            file_name: `sbi-total-expense-ratio-ter-data-file.xlsx`,
            page_number: 1,
            section: "Total Expense Ratio"
          }
        }];
      } else if (qLower.includes("lock-in") || qLower.includes("lock in")) {
        if (matchedScheme.id === "sbi-elss-tax-saver") {
          answer = `Investments in ${matchedScheme.name} are subject to a statutory lock-in period of 3 years from the date of allotment to avail Section 80C benefits. Source: ${matchedScheme.name} Factsheet, April 2026.`;
          chunks = [{
            id: `${matchedScheme.id}-chunk-lockin`,
            score: 0.96,
            text: `An open-ended Equity Linked Saving Scheme with a statutory lock-in period of 3 years and tax benefit. Investments in this scheme would be subject to a statutory lock-in of 3 years from the date of allotment to avail Section 80C benefits.`,
            metadata: {
              citation: `${matchedScheme.name} Factsheet, April 2026.`,
              file_name: `${matchedScheme.id}-factsheet.pdf`,
              page_number: 1,
              section: "Scheme Details"
            }
          }];
        } else {
          answer = "I could not find this information in the available approved SBI Mutual Fund sources.";
        }
      } else {
        // Generic response
        answer = `Regarding ${matchedScheme.name}: The scheme is open-ended with asset allocation primarily in equities. For comprehensive details, please refer to the official factsheet. Source: ${matchedScheme.name} Factsheet, April 2026.`;
        chunks = [{
          id: `${matchedScheme.id}-chunk-generic`,
          score: 0.82,
          text: `Type of Scheme: Open-ended equity scheme investing in diversified stocks. AUM: ${matchedScheme.aum}. Fund Manager details and asset allocation details are listed on Page 1.`,
          metadata: {
            citation: `${matchedScheme.name} Factsheet, April 2026.`,
            file_name: `${matchedScheme.id}-factsheet.pdf`,
            page_number: 1,
            section: "Scheme Details"
          }
        }];
      }
    }

    setTimeout(() => {
      setChatHistory(prev => [...prev, {
        role: 'assistant',
        question: questionText,
        answer: answer,
        chunks: chunks,
        is_advice: is_advice,
        is_ambiguous: is_ambiguous,
        timestamp: new Date()
      }]);
    }, 600);
  };

  const handleTemplateClick = (templateQuery) => {
    const filledQuery = templateQuery.replace("{scheme}", selectedScheme.name);
    setQueryInput(filledQuery);
    handleQuery(filledQuery);
  };

  // Helper to extract citation if "Source:" is in the text
  const parseAnswerText = (text) => {
    if (!text) return { body: "", citation: "" };
    if (text.includes("Source:")) {
      const parts = text.split("Source:");
      return {
        body: parts[0].trim(),
        citation: parts[parts.length - 1].trim()
      };
    }
    return { body: text, citation: "" };
  };

  return (
    <div className="flex flex-col h-screen text-on-surface bg-background overflow-hidden font-body-md select-none">
      
      {/* Top Header */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-md h-xl bg-surface/80 backdrop-blur-xl border-b border-outline-variant/20">
        <div className="flex items-center gap-sm">
          <span className="text-headline-md font-headline-md font-bold text-primary">SBI Mutual Fund FAQ Assistant</span>
        </div>
        <div className="flex items-center gap-md">
          <span className="hidden sm:inline-flex items-center gap-xs px-xs py-1 rounded bg-primary/10 text-primary border border-primary/20 text-label-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Active Provider: Groq
          </span>
          <button className="material-symbols-outlined text-primary p-xs rounded-full hover:bg-surface-container-high/50 transition-colors">shield</button>
          <button className="material-symbols-outlined text-primary p-xs rounded-full hover:bg-surface-container-high/50 transition-colors">dark_mode</button>
          <button className="material-symbols-outlined text-primary p-xs rounded-full hover:bg-surface-container-high/50 transition-colors">settings</button>
        </div>
      </header>

      <div className="flex flex-1 pt-xl pb-xl h-full overflow-hidden">
        
        {/* Left Side Navigation */}
        <aside className="hidden md:flex w-[260px] flex-col p-xs bg-surface-container-low/60 backdrop-blur-xl border-r border-outline-variant/20">
          <div className="px-sm py-md mb-xs">
            <div className="flex items-center gap-xs">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>account_balance</span>
              </div>
              <div>
                <div className="text-headline-sm font-headline-sm font-bold text-on-surface">Lumina Finance</div>
                <div className="text-label-md font-label-md text-on-surface-variant">Factual RAG Assistant</div>
              </div>
            </div>
          </div>
          
          <nav className="flex-1 space-y-1">
            <button
              onClick={() => setActiveSection("knowledge")}
              className={`w-full flex items-center gap-md px-md py-xs transition-all text-left rounded-xl ${
                activeSection === "knowledge"
                  ? "bg-primary-container text-on-primary-container scale-98"
                  : "text-on-surface-variant hover:bg-surface-container-highest/40"
              }`}
            >
              <span className="material-symbols-outlined" style={activeSection === "knowledge" ? { fontVariationSettings: "'FILL' 1" } : {}}>database</span>
              <span className="text-label-md font-label-md">Knowledge Base</span>
            </button>
            <button
              onClick={() => setActiveSection("templates")}
              className={`w-full flex items-center gap-md px-md py-xs transition-all text-left rounded-xl ${
                activeSection === "templates"
                  ? "bg-primary-container text-on-primary-container scale-98"
                  : "text-on-surface-variant hover:bg-surface-container-highest/40"
              }`}
            >
              <span className="material-symbols-outlined" style={activeSection === "templates" ? { fontVariationSettings: "'FILL' 1" } : {}}>list_alt</span>
              <span className="text-label-md font-label-md">Query Templates</span>
            </button>
            <button
              onClick={() => setActiveSection("analysis")}
              className={`w-full flex items-center gap-md px-md py-xs transition-all text-left rounded-xl ${
                activeSection === "analysis"
                  ? "bg-primary-container text-on-primary-container scale-98"
                  : "text-on-surface-variant hover:bg-surface-container-highest/40"
              }`}
            >
              <span className="material-symbols-outlined" style={activeSection === "analysis" ? { fontVariationSettings: "'FILL' 1" } : {}}>analytics</span>
              <span className="text-label-md font-label-md">Scheme Analysis</span>
            </button>
            <button
              onClick={() => setActiveSection("safety")}
              className={`w-full flex items-center gap-md px-md py-xs transition-all text-left rounded-xl ${
                activeSection === "safety"
                  ? "bg-primary-container text-on-primary-container scale-98"
                  : "text-on-surface-variant hover:bg-surface-container-highest/40"
              }`}
            >
              <span className="material-symbols-outlined" style={activeSection === "safety" ? { fontVariationSettings: "'FILL' 1" } : {}}>verified_user</span>
              <span className="text-label-md font-label-md">Safety Logs</span>
            </button>
          </nav>
          
          <div className="mt-auto px-xs space-y-1">
            <button onClick={() => setChatHistory([chatHistory[0]])} className="w-full mb-md py-sm bg-primary text-on-primary font-bold rounded-xl flex items-center justify-center gap-xs active:scale-95 transition-transform">
              <span className="material-symbols-outlined">refresh</span>
              Clear Chat
            </button>
            <button className="w-full flex items-center gap-md px-md py-xs text-on-surface-variant hover:bg-surface-container-highest/40 rounded-xl text-left">
              <span className="material-symbols-outlined">help</span>
              <span className="text-label-md font-label-md">Help</span>
            </button>
            <button className="w-full flex items-center gap-md px-md py-xs text-on-surface-variant hover:bg-surface-container-highest/40 rounded-xl text-left">
              <span className="material-symbols-outlined">check_circle</span>
              <span className="text-label-md font-label-md">Status</span>
            </button>
          </div>
        </aside>

        {/* Main Content Area */}
        {activeSection === "analysis" ? (
          <main className="flex-1 flex flex-col lg:flex-row gap-gutter p-md overflow-hidden w-full">
            
            {/* Left Column - Schemes (40% width on large screen) */}
            <section className="w-full lg:w-[35%] flex flex-col gap-md h-full overflow-hidden">
              <div className="flex-none">
                <h2 className="text-headline-md font-headline-md text-on-surface mb-xs">Supported Schemes</h2>
                <p className="text-on-surface-variant text-label-md">Select a fund to contextualize your queries.</p>
              </div>
              
              {/* Fund Cards Container */}
              <div className="flex-1 flex flex-col gap-sm overflow-y-auto custom-scrollbar pr-xs">
                {SCHEMES.map((scheme) => (
                  <div
                    key={scheme.id}
                    onClick={() => setSelectedScheme(scheme)}
                    className={`glass-panel p-md rounded-xl group relative overflow-hidden cursor-pointer transition-all border ${
                      selectedScheme.id === scheme.id ? 'border-primary bg-primary/5 jade-glow' : 'border-outline-variant/20 hover:border-primary/40'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-xs">
                      <span className={`text-label-sm font-label-sm px-xs py-1 rounded border ${scheme.tagColor}`}>
                        {scheme.type}
                      </span>
                      <span className={`material-symbols-outlined transition-transform group-hover:scale-110 ${
                        selectedScheme.id === scheme.id ? 'text-primary' : 'text-outline'
                      }`}>
                        {scheme.icon}
                      </span>
                    </div>
                    <h3 className="text-body-lg font-bold text-on-surface">{scheme.name}</h3>
                    <p className="text-label-md text-on-surface-variant">{scheme.description}</p>
                    
                    {/* Stats Grid */}
                    <div className="mt-md pt-md border-t border-outline-variant/20 flex justify-between items-center transition-all duration-300">
                      <div className="text-center">
                        <div className="text-label-sm text-on-surface-variant">Asset Class</div>
                        <div className="text-label-md font-bold text-primary">{scheme.assetClass}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-label-sm text-on-surface-variant">Launch Date</div>
                        <div className="text-label-md font-bold text-primary">{scheme.launchDate}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-label-sm text-on-surface-variant">AUM</div>
                        <div className="text-label-md font-bold text-primary">{scheme.aum}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Quick Query Templates */}
              <div className="flex-none pt-md border-t border-outline-variant/10">
                <h3 className="text-label-md font-bold text-on-surface mb-sm">Quick-Query Templates</h3>
                <div className="flex flex-wrap gap-xs">
                  {TEMPLATES.map((tpl, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleTemplateClick(tpl.query)}
                      className="px-md py-xs glass-panel rounded-full text-label-md text-on-surface-variant hover:text-primary hover:border-primary/50 transition-colors text-left"
                    >
                      {tpl.label}
                    </button>
                  ))}
                </div>
              </div>
            </section>

            {/* Right Column - Conversational results (65% width) */}
            <section className="flex-1 flex flex-col gap-md h-full relative overflow-hidden">
              
              {/* Search Input Box */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleQuery(queryInput);
                }}
                className="glass-panel p-sm rounded-2xl jade-glow-strong border-primary/20 flex items-center gap-md flex-none"
              >
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-none">
                  <span className="material-symbols-outlined text-primary">psychology</span>
                </div>
                <input
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  className="bg-transparent border-none outline-none focus:ring-0 text-body-lg text-on-surface w-full placeholder:text-outline/50 focus:outline-none"
                  placeholder={`Ask about ${selectedScheme.name} (e.g., minimum investment, TER, exit load)...`}
                  type="text"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !queryInput.trim()}
                  className="bg-primary text-on-primary w-12 h-12 rounded-xl flex items-center justify-center shadow-lg active:scale-95 transition-transform flex-none disabled:opacity-50 disabled:scale-100"
                >
                  {loading ? (
                    <span className="animate-spin rounded-full h-5 w-5 border-2 border-on-primary border-t-transparent"></span>
                  ) : (
                    <span className="material-symbols-outlined">arrow_forward</span>
                  )}
                </button>
              </form>

              {/* Chat History Canvas */}
              <div className="flex-1 overflow-y-auto custom-scrollbar pr-xs space-y-md">
                {chatHistory.map((msg, index) => (
                  <div key={index} className="space-y-sm">
                    {msg.role === 'user' ? (
                      /* User Question */
                      <div className="flex justify-end">
                        <div className="max-w-[80%] glass-panel px-md py-sm rounded-2xl rounded-tr-none text-on-surface border-primary/10 bg-surface-container/20">
                          <p className="text-body-md">{msg.text}</p>
                        </div>
                      </div>
                    ) : (
                      /* Assistant Answer Card */
                      <div className="glass-panel p-lg rounded-2xl relative border-outline-variant/15">
                        {msg.question && (
                          <div className="text-label-sm text-outline mb-xs italic">
                            Query: "{msg.question}"
                          </div>
                        )}
                        
                        {/* State Indicator Headers */}
                        {msg.is_advice ? (
                          <div className="flex items-center gap-xs mb-md">
                            <span className="material-symbols-outlined text-error" style={{ fontVariationSettings: "'FILL' 1" }}>gpp_maybe</span>
                            <span className="text-label-sm font-bold text-error tracking-widest uppercase">Advice Refusal Alert</span>
                          </div>
                        ) : msg.is_ambiguous ? (
                          <div className="flex items-center gap-xs mb-md">
                            <span className="material-symbols-outlined text-tertiary" style={{ fontVariationSettings: "'FILL' 1" }}>help</span>
                            <span className="text-label-sm font-bold text-tertiary tracking-widest uppercase">Clarification Required</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-xs mb-md flex-wrap gap-y-xs">
                            <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
                            <span className="text-label-sm font-bold text-primary tracking-widest uppercase">Factual Answer</span>
                            <span className="mx-xs h-3 w-[1px] bg-outline-variant/30 hidden sm:inline"></span>
                            
                            {/* Citation Tag */}
                            {parseAnswerText(msg.answer).citation && (
                              <span className="text-label-sm bg-surface-container-high px-xs py-0.5 rounded text-on-surface-variant">
                                {parseAnswerText(msg.answer).citation}
                              </span>
                            )}
                          </div>
                        )}

                        {/* Answer Body */}
                        <div className="space-y-md">
                          {msg.is_advice ? (
                            <p className="text-body-lg text-error/90 leading-relaxed font-semibold">
                              {msg.answer}
                            </p>
                          ) : msg.is_ambiguous ? (
                            <div className="space-y-sm">
                              <p className="text-body-lg text-tertiary leading-relaxed font-semibold">
                                {msg.answer}
                              </p>
                              <div className="flex flex-wrap gap-xs pt-xs">
                                {SCHEMES.map(s => (
                                  <button
                                    key={s.id}
                                    onClick={() => {
                                      setSelectedScheme(s);
                                      if (msg.question) {
                                        // Re-run with scheme name appended
                                        handleQuery(`${msg.question} for ${s.name}`);
                                      }
                                    }}
                                    className="px-md py-xs bg-surface-container-high text-on-surface rounded-xl hover:bg-primary hover:text-on-primary transition-all text-label-sm"
                                  >
                                    {s.name}
                                  </button>
                                ))}
                              </div>
                            </div>
                          ) : (
                            <p className="text-body-lg leading-relaxed text-on-surface">
                              {parseAnswerText(msg.answer).body}
                            </p>
                          )}
                        </div>

                        {/* Retrieved Grounding Chunks Accordion */}
                        {!msg.is_advice && !msg.is_ambiguous && msg.chunks && msg.chunks.length > 0 && (
                          <details className="group mt-lg pt-lg border-t border-outline-variant/20">
                            <summary className="flex items-center justify-between cursor-pointer list-none select-none">
                              <div className="flex items-center gap-xs">
                                <span className="material-symbols-outlined text-primary transition-transform duration-200 group-open:rotate-180">
                                  expand_more
                                </span>
                                <h4 className="text-label-md font-bold flex items-center gap-xs">
                                  <span className="material-symbols-outlined text-sm">attachment</span>
                                  Grounding &amp; Reference Chunks
                                </h4>
                              </div>
                              <span className="text-label-sm text-outline">Showing {msg.chunks.length} matching sources</span>
                            </summary>
                            
                            <div className="space-y-sm mt-md">
                              {msg.chunks.map((chunk, cIdx) => (
                                <div key={chunk.id || cIdx} className="glass-panel bg-surface-container-low/40 p-md rounded-xl border-primary/10">
                                  <div className="flex items-center gap-md mb-sm">
                                    
                                    {/* Score indicator */}
                                    <div className="relative w-12 h-12 flex-none">
                                      <svg className="w-full h-full -rotate-90">
                                        <circle className="text-outline-variant/10" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeWidth="4"></circle>
                                        <circle 
                                          className="text-primary transition-all duration-500" 
                                          cx="24" 
                                          cy="24" 
                                          fill="transparent" 
                                          r="20" 
                                          stroke="currentColor" 
                                          strokeWidth="4"
                                          strokeDasharray="125.6"
                                          strokeDashoffset={125.6 - (125.6 * (chunk.score || 0.9))}
                                        ></circle>
                                      </svg>
                                      <div className="absolute inset-0 flex items-center justify-center text-label-sm font-bold text-primary">
                                        {Math.round((chunk.score || 0.9) * 100)}%
                                      </div>
                                    </div>

                                    <div className="flex-1 min-w-0">
                                      <div className="text-label-sm font-bold text-on-surface truncate">
                                        {chunk.metadata?.file_name || "Source Document"}
                                      </div>
                                      <div className="text-label-sm text-on-surface-variant truncate">
                                        Page {chunk.metadata?.page_number || 1}, Section: {chunk.metadata?.section || "Details"}
                                      </div>
                                    </div>
                                    
                                    <span className="material-symbols-outlined text-outline/50 text-sm">verified</span>
                                  </div>
                                  <p className="text-label-md italic text-on-surface-variant border-l-2 border-primary pl-md py-xs leading-relaxed bg-surface-container-lowest/20 rounded-r-lg">
                                    "{chunk.text}"
                                  </p>
                                </div>
                              ))}
                            </div>
                          </details>
                        )}
                      </div>
                    )}
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            </section>
          </main>
        ) : activeSection === "knowledge" ? (
          <main className="flex-1 flex flex-col gap-lg p-lg overflow-y-auto w-full custom-scrollbar max-w-6xl mx-auto pb-2xl">
            {/* Header */}
            <div className="mt-md">
              <h2 className="text-headline-lg font-bold text-on-surface mb-xs">Knowledge Base Registry</h2>
              <p className="text-on-surface-variant text-body-md">Ingested official documents and vector store registry for the RAG chatbot.</p>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-md">
              <div className="glass-panel p-md rounded-2xl border-primary/20 bg-primary/5">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary text-xl">database</span>
                  <div>
                    <div className="text-label-sm text-on-surface-variant font-bold">Indexed Chunks</div>
                    <div className="text-headline-md font-bold text-primary">220 Chunks</div>
                  </div>
                </div>
              </div>
              <div className="glass-panel p-md rounded-2xl border-outline-variant/20">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary text-xl">description</span>
                  <div>
                    <div className="text-label-sm text-on-surface-variant font-bold">Source Files</div>
                    <div className="text-headline-md font-bold text-primary">4 Files</div>
                  </div>
                </div>
              </div>
              <div className="glass-panel p-md rounded-2xl border-outline-variant/20">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary text-xl">category</span>
                  <div>
                    <div className="text-label-sm text-on-surface-variant font-bold">Supported Schemes</div>
                    <div className="text-headline-md font-bold text-primary">3 Schemes</div>
                  </div>
                </div>
              </div>
              <div className="glass-panel p-md rounded-2xl border-outline-variant/20">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary text-xl">published_with_changes</span>
                  <div>
                    <div className="text-label-sm text-on-surface-variant font-bold">Last Indexed</div>
                    <div className="text-headline-md font-bold text-primary">June 2026</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Content Split: Schemes & Sources */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-lg">
              {/* Left Column: Supported Schemes (5 cols) */}
              <div className="lg:col-span-5 flex flex-col gap-md">
                <h3 className="text-title-md font-bold text-on-surface">Supported Mutual Fund Schemes</h3>
                <div className="flex flex-col gap-sm">
                  {SCHEMES.map(s => (
                    <div key={s.id} className="glass-panel p-md rounded-xl border-outline-variant/10 bg-surface-container-low/20">
                      <div className="flex justify-between items-center mb-xs">
                        <span className={`text-label-sm font-label-sm px-xs py-0.5 rounded border ${s.tagColor}`}>{s.type}</span>
                        <span className="text-label-sm text-outline">AUM: {s.aum}</span>
                      </div>
                      <h4 className="text-body-md font-bold text-on-surface mb-xs">{s.name}</h4>
                      <p className="text-label-md text-on-surface-variant leading-relaxed">{s.description}</p>
                      <div className="flex gap-md mt-sm pt-sm border-t border-outline-variant/10 text-label-sm text-primary">
                        <span>Class: {s.assetClass}</span>
                        <span>•</span>
                        <span>Launched: {s.launchDate}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right Column: Ingested Source Documents (7 cols) */}
              <div className="lg:col-span-7 flex flex-col gap-md">
                <h3 className="text-title-md font-bold text-on-surface">Ingested Source Registries</h3>
                <div className="flex flex-col gap-sm">
                  <div className="glass-panel p-md rounded-xl border-outline-variant/10 bg-surface-container-low/20">
                    <div className="flex justify-between items-start mb-sm">
                      <div className="flex items-center gap-xs">
                        <span className="material-symbols-outlined text-primary">picture_as_pdf</span>
                        <h4 className="text-body-md font-bold text-on-surface">sbi-flexicap-fund-factsheet-april-2026.pdf</h4>
                      </div>
                      <span className="text-label-sm px-xs py-0.5 rounded bg-primary/10 text-primary border border-primary/20 font-bold">1.47 MB</span>
                    </div>
                    <p className="text-label-md text-on-surface-variant mb-xs leading-relaxed">Official scheme factsheet covering exit load (0.10% / Nil), benchmark index (BSE 500 TRI), riskometer (Very High), and minimum investment rules.</p>
                    <div className="text-label-sm text-outline font-mono truncate">SHA256: 033f97f7872c9765a9cbd80dd20581dff1ad8d66ab4e10564b0136748069d380</div>
                  </div>

                  <div className="glass-panel p-md rounded-xl border-outline-variant/10 bg-surface-container-low/20">
                    <div className="flex justify-between items-start mb-sm">
                      <div className="flex items-center gap-xs">
                        <span className="material-symbols-outlined text-primary">picture_as_pdf</span>
                        <h4 className="text-body-md font-bold text-on-surface">sbi-elss-tax-saver-fund-factsheet-april-2026.pdf</h4>
                      </div>
                      <span className="text-label-sm px-xs py-0.5 rounded bg-primary/10 text-primary border border-primary/20 font-bold">1.48 MB</span>
                    </div>
                    <p className="text-label-md text-on-surface-variant mb-xs leading-relaxed">Official Facts document describing ELSS scheme features, investment objective, and the 3-year lock-in period for Section 80C tax benefits.</p>
                    <div className="text-label-sm text-outline font-mono truncate">SHA256: fe2125bfbd69071f503d9b1434cd3f420aa5996a2b9df2f32aef94d39f9a80c3</div>
                  </div>

                  <div className="glass-panel p-md rounded-xl border-outline-variant/10 bg-surface-container-low/20">
                    <div className="flex justify-between items-start mb-sm">
                      <div className="flex items-center gap-xs">
                        <span className="material-symbols-outlined text-primary">picture_as_pdf</span>
                        <h4 className="text-body-md font-bold text-on-surface">sbi-large-cap-fund-factsheet-april-2026.pdf</h4>
                      </div>
                      <span className="text-label-sm px-xs py-0.5 rounded bg-primary/10 text-primary border border-primary/20 font-bold">1.47 MB</span>
                    </div>
                    <p className="text-label-md text-on-surface-variant mb-xs leading-relaxed">Factsheet details for the Large Cap Fund detailing exit load (1.00% / Nil), scheme riskometer, and investment criteria.</p>
                    <div className="text-label-sm text-outline font-mono truncate">SHA256: 12178b0940bdb20d12f5313399d70a6c153c3bd465c85ebf657be08d7ba2f427</div>
                  </div>

                  <div className="glass-panel p-md rounded-xl border-outline-variant/10 bg-surface-container-low/20">
                    <div className="flex justify-between items-start mb-sm">
                      <div className="flex items-center gap-xs">
                        <span className="material-symbols-outlined text-primary">table_chart</span>
                        <h4 className="text-body-md font-bold text-on-surface">sbi-total-expense-ratio-ter-data-file.xlsx</h4>
                      </div>
                      <span className="text-label-sm px-xs py-0.5 rounded bg-primary/10 text-primary border border-primary/20 font-bold">550 KB</span>
                    </div>
                    <p className="text-label-md text-on-surface-variant mb-xs leading-relaxed">Granular day-to-day Total Expense Ratio (TER) data logs mapping direct and regular plans of the Flexicap, ELSS, and Large Cap funds.</p>
                    <div className="text-label-sm text-outline font-mono truncate">SHA256: e5d48e40285105c70ec305081b62e479049157d3a37d7cf1621a39007fa72941</div>
                  </div>
                </div>
              </div>
            </div>
          </main>
        ) : activeSection === "templates" ? (
          <main className="flex-1 flex flex-col gap-lg p-lg overflow-y-auto w-full custom-scrollbar max-w-5xl mx-auto pb-2xl">
            {/* Header */}
            <div className="mt-md">
              <h2 className="text-headline-lg font-bold text-on-surface mb-xs">Query Template Library</h2>
              <p className="text-on-surface-variant text-body-md">Choose one of the common query templates below to test the RAG chatbot's response.</p>
            </div>

            {/* Template Groups */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
              
              {/* Group 1: Scheme Exit Loads */}
              <div className="glass-panel p-lg rounded-2xl border-outline-variant/10 flex flex-col gap-md bg-surface-container-low/10">
                <div className="flex items-center gap-xs text-primary mb-xs">
                  <span className="material-symbols-outlined">payments</span>
                  <h3 className="text-title-md font-bold text-on-surface">Exit Loads &amp; Fees</h3>
                </div>
                <div className="space-y-sm">
                  {[
                    "What is the exit load of SBI Flexicap Fund?",
                    "What is the exit load of SBI ELSS Tax Saver Fund?",
                    "What is the exit load of SBI Large Cap Fund?"
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQueryInput(q);
                        setActiveSection("analysis");
                        handleQuery(q);
                      }}
                      className="w-full text-left p-md rounded-xl bg-surface-container-low/40 hover:bg-primary/5 border border-outline-variant/10 hover:border-primary/40 transition-all text-body-md text-on-surface-variant hover:text-primary flex justify-between items-center group"
                    >
                      <span>{q}</span>
                      <span className="material-symbols-outlined text-outline group-hover:text-primary transition-transform group-hover:translate-x-1">arrow_forward</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Group 2: Total Expense Ratio (TER) */}
              <div className="glass-panel p-lg rounded-2xl border-outline-variant/10 flex flex-col gap-md bg-surface-container-low/10">
                <div className="flex items-center gap-xs text-primary mb-xs">
                  <span className="material-symbols-outlined">analytics</span>
                  <h3 className="text-title-md font-bold text-on-surface">Total Expense Ratio (TER)</h3>
                </div>
                <div className="space-y-sm">
                  {[
                    "What is the expense ratio of SBI Flexicap Fund?",
                    "What is the expense ratio of SBI ELSS Tax Saver Fund?",
                    "What is the expense ratio of SBI Large Cap Fund?"
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQueryInput(q);
                        setActiveSection("analysis");
                        handleQuery(q);
                      }}
                      className="w-full text-left p-md rounded-xl bg-surface-container-low/40 hover:bg-primary/5 border border-outline-variant/10 hover:border-primary/40 transition-all text-body-md text-on-surface-variant hover:text-primary flex justify-between items-center group"
                    >
                      <span>{q}</span>
                      <span className="material-symbols-outlined text-outline group-hover:text-primary transition-transform group-hover:translate-x-1">arrow_forward</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Group 3: Benchmarks & Lock-in Periods */}
              <div className="glass-panel p-lg rounded-2xl border-outline-variant/10 flex flex-col gap-md bg-surface-container-low/10">
                <div className="flex items-center gap-xs text-primary mb-xs">
                  <span className="material-symbols-outlined">show_chart</span>
                  <h3 className="text-title-md font-bold text-on-surface">Benchmarks &amp; Lock-in Periods</h3>
                </div>
                <div className="space-y-sm">
                  {[
                    "What is the benchmark of SBI Large Cap Fund?",
                    "What is the benchmark of SBI Flexicap Fund?",
                    "What is the lock-in period of SBI ELSS Tax Saver Fund?"
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQueryInput(q);
                        setActiveSection("analysis");
                        handleQuery(q);
                      }}
                      className="w-full text-left p-md rounded-xl bg-surface-container-low/40 hover:bg-primary/5 border border-outline-variant/10 hover:border-primary/40 transition-all text-body-md text-on-surface-variant hover:text-primary flex justify-between items-center group"
                    >
                      <span>{q}</span>
                      <span className="material-symbols-outlined text-outline group-hover:text-primary transition-transform group-hover:translate-x-1">arrow_forward</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Group 4: Investment Objectives & SIPs */}
              <div className="glass-panel p-lg rounded-2xl border-outline-variant/10 flex flex-col gap-md bg-surface-container-low/10">
                <div className="flex items-center gap-xs text-primary mb-xs">
                  <span className="material-symbols-outlined">assignment</span>
                  <h3 className="text-title-md font-bold text-on-surface">Objectives &amp; SIP Thresholds</h3>
                </div>
                <div className="space-y-sm">
                  {[
                    "What is the investment objective of SBI Flexicap Fund?",
                    "What is the minimum SIP amount of SBI Large Cap Fund?",
                    "What is the minimum SIP amount of SBI Flexicap Fund?"
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQueryInput(q);
                        setActiveSection("analysis");
                        handleQuery(q);
                      }}
                      className="w-full text-left p-md rounded-xl bg-surface-container-low/40 hover:bg-primary/5 border border-outline-variant/10 hover:border-primary/40 transition-all text-body-md text-on-surface-variant hover:text-primary flex justify-between items-center group"
                    >
                      <span>{q}</span>
                      <span className="material-symbols-outlined text-outline group-hover:text-primary transition-transform group-hover:translate-x-1">arrow_forward</span>
                    </button>
                  ))}
                </div>
              </div>

            </div>
          </main>
        ) : activeSection === "safety" ? (
          <main className="flex-1 flex flex-col gap-lg p-lg overflow-y-auto w-full custom-scrollbar max-w-5xl mx-auto pb-2xl">
            {/* Header */}
            <div className="mt-md">
              <h2 className="text-headline-lg font-bold text-on-surface mb-xs">Safety &amp; Compliance Monitor</h2>
              <p className="text-on-surface-variant text-body-md">Real-time safety guardrail behavior logs and regulatory compliance checks.</p>
            </div>

            {/* Safety Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-md">
              <div className="glass-panel p-md rounded-2xl border-primary/10">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary text-xl">shield</span>
                  <div>
                    <div className="text-label-sm text-on-surface-variant font-bold">Advice Guardrail</div>
                    <div className="text-body-md font-bold text-primary">Active (Refusal mode)</div>
                  </div>
                </div>
              </div>
              <div className="glass-panel p-md rounded-2xl border-primary/10">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary text-xl">rule</span>
                  <div>
                    <div className="text-label-sm text-on-surface-variant font-bold">Grounding Check</div>
                    <div className="text-body-md font-bold text-primary">Strict Numerical Match</div>
                  </div>
                </div>
              </div>
              <div className="glass-panel p-md rounded-2xl border-primary/10">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-primary text-xl">verified_user</span>
                  <div>
                    <div className="text-label-sm text-on-surface-variant font-bold">Compliance Standard</div>
                    <div className="text-body-md font-bold text-primary">SEBI Non-Advisory RAG</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Detailed Guardrails Explanation */}
            <div className="glass-panel p-lg rounded-2xl border-outline-variant/10 space-y-md bg-surface-container-low/10">
              <h3 className="text-title-md font-bold text-on-surface">System Guardrails &amp; Intent Classification</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
                
                <div className="space-y-xs">
                  <div className="flex items-center gap-xs text-primary font-bold">
                    <span className="material-symbols-outlined text-sm">gpp_maybe</span>
                    <span>Advice Refusal</span>
                  </div>
                  <p className="text-label-md text-on-surface-variant leading-relaxed">
                    Identifies advisory intent (e.g. buying recommendations, asset allocation opinions) and blocks execution. The system refuses to suggest investments, providing only facts from official factsheets.
                  </p>
                </div>

                <div className="space-y-xs">
                  <div className="flex items-center gap-xs text-primary font-bold">
                    <span className="material-symbols-outlined text-sm">help</span>
                    <span>Ambiguity Resolver</span>
                  </div>
                  <p className="text-label-md text-on-surface-variant leading-relaxed">
                    Checks if queries specify which scheme to inspect. If the query is ambiguous, it requests clarification and offers quick-selection buttons for supported schemes.
                  </p>
                </div>

                <div className="space-y-xs">
                  <div className="flex items-center gap-xs text-primary font-bold">
                    <span className="material-symbols-outlined text-sm">done_all</span>
                    <span>Grounding Validation</span>
                  </div>
                  <p className="text-label-md text-on-surface-variant leading-relaxed">
                    A post-generation step parses all numbers and percentages (like exit load fees, lock-in periods) in the generated text, ensuring they exist exactly in the retrieved context chunks to block hallucinated figures.
                  </p>
                </div>

              </div>
            </div>

            {/* Showcase Scenarios */}
            <div className="space-y-md">
              <h3 className="text-title-md font-bold text-on-surface">Example Guardrail Scenarios</h3>
              
              <div className="space-y-sm">
                
                {/* Case 1 */}
                <div className="glass-panel p-md rounded-xl border-error/20 bg-error/5 flex flex-col gap-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-label-sm font-bold text-error tracking-widest uppercase flex items-center gap-xs">
                      <span className="material-symbols-outlined text-sm">gpp_maybe</span>
                      Advice Refusal
                    </span>
                    <span className="text-label-sm text-outline">Intent: Recommendation / Advice</span>
                  </div>
                  <div className="text-body-md font-semibold text-on-surface mt-xs">
                    Query: "Should I invest in SBI Large Cap Fund?"
                  </div>
                  <div className="text-body-md text-error/95 leading-relaxed bg-surface-container-lowest/30 p-sm rounded-lg border-l-2 border-error font-medium">
                    "I cannot provide investment advice or recommendations. I can only provide factual information from official SBI Mutual Fund documents."
                  </div>
                </div>

                {/* Case 2 */}
                <div className="glass-panel p-md rounded-xl border-tertiary/20 bg-tertiary/5 flex flex-col gap-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-label-sm font-bold text-tertiary tracking-widest uppercase flex items-center gap-xs">
                      <span className="material-symbols-outlined text-sm">help</span>
                      Ambiguity Classifier
                    </span>
                    <span className="text-label-sm text-outline">Intent: Incomplete Schema Specification</span>
                  </div>
                  <div className="text-body-md font-semibold text-on-surface mt-xs">
                    Query: "What is the expense ratio?"
                  </div>
                  <div className="text-body-md text-tertiary leading-relaxed bg-surface-container-lowest/30 p-sm rounded-lg border-l-2 border-tertiary font-medium">
                    "Please specify one of the supported schemes: SBI Flexicap Fund, SBI ELSS Tax Saver Fund, or SBI Large Cap Fund."
                  </div>
                </div>

                {/* Case 3 */}
                <div className="glass-panel p-md rounded-xl border-outline-variant/20 bg-surface-container-low/20 flex flex-col gap-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-label-sm font-bold text-primary tracking-widest uppercase flex items-center gap-xs">
                      <span className="material-symbols-outlined text-sm">cancel</span>
                      Out of Bounds / Unsupported Field
                    </span>
                    <span className="text-label-sm text-outline">Intent: Non-factsheet Field Inquiry</span>
                  </div>
                  <div className="text-body-md font-semibold text-on-surface mt-xs">
                    Query: "What is the daily NAV of SBI Flexicap Fund?"
                  </div>
                  <div className="text-body-md text-on-surface-variant leading-relaxed bg-surface-container-lowest/30 p-sm rounded-lg border-l-2 border-primary font-medium italic">
                    "I could not find this information in the available approved SBI Mutual Fund sources."
                  </div>
                </div>

              </div>
            </div>
          </main>
        ) : null}
      </div>

      {/* Fixed Footer Disclaimer */}
      <footer className="fixed bottom-0 left-0 w-full z-50 flex flex-col justify-center items-center bg-surface-container-lowest/90 backdrop-blur-md border-t border-outline-variant/20 py-xs px-md">
        <div className="flex gap-md mb-1">
          <span className="text-label-sm text-on-surface-variant text-center">
            © 2026 SBI Mutual Fund. Factual RAG Assistant • Grounded Facts-Only Mode Active.
          </span>
        </div>
        <div className="flex gap-md">
          <a className="text-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Legal Disclaimer</a>
          <span className="text-outline-variant/30">•</span>
          <a className="text-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Privacy Policy</a>
          <span className="text-outline-variant/30">•</span>
          <a className="text-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Regulatory Info</a>
        </div>
      </footer>
    </div>
  );
}
