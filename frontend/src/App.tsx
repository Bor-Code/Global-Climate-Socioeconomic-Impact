import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { Send, Activity, Globe, HeartPulse, MessageCircle, X, Brain, Sparkles, TrendingUp, Leaf } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ScatterChart, Scatter, ZAxis, CartesianGrid } from 'recharts'
import './App.css'

const API_URL = "http://localhost:8000"

function App() {
  const [summary, setSummary] = useState<any>(null)
  const [chartData, setChartData] = useState<any>({ top10: [], scatter: [] })
  
  const [features, setFeatures] = useState({
    gdp_per_capita: 45000.0,
    social_support: 1.45,
    life_expectancy: 0.85,
    freedom: 0.65,
    corruption: 0.15
  })
  const [prediction, setPrediction] = useState<number | null>(null)
  const [predictLoading, setPredictLoading] = useState(false)
  
  const [messages, setMessages] = useState<any[]>([])
  const [prompt, setPrompt] = useState("")
  const [chatLoading, setChatLoading] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    axios.get(`${API_URL}/api/data/summary`)
      .then(res => setSummary(res.data))
      .catch(err => console.error("Could not load summary", err))
    axios.get(`${API_URL}/api/data/charts`)
      .then(res => setChartData(res.data))
      .catch(err => console.error("Could not load charts", err))
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const [activeTab, setActiveTab] = useState('Dashboard')

  const handlePredict = async () => {
    setPredictLoading(true)
    try {
      const payload = {
        gdp_per_capita: Number(features.gdp_per_capita) || 45000.0,
        social_support: Number(features.social_support) || 1.45,
        life_expectancy: Number(features.life_expectancy) || 0.85,
        freedom: Number(features.freedom) || 0.65,
        corruption: Number(features.corruption) || 0.15
      }
      const res = await axios.post(`${API_URL}/predict`, payload)
      setPrediction(res.data.predicted_happiness_score)
    } catch (err) {
      console.error(err)
      alert("Prediction error. Check backend.")
    } finally {
      setPredictLoading(false)
    }
  }

  const handleChat = async () => {
    if (!prompt.trim()) return
    const newMessages = [...messages, { role: 'user', content: prompt }]
    setMessages(newMessages)
    setPrompt("")
    setChatLoading(true)
    try {
      const res = await axios.post(`${API_URL}/api/chat`, { prompt })
      setMessages([...newMessages, { role: 'ai', content: res.data.answer }])
    } catch {
      setMessages([...newMessages, { role: 'ai', content: "Network error. Try again." }])
    } finally {
      setChatLoading(false)
    }
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{payload[0].payload.country_name}</p>
          <p className="tooltip-value">{payload[0].value.toFixed(2)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="app-root">
      {/* Ambient Gradient Orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-brand">
          <Sparkles size={24} />
          <span>ClimateIQ</span>
        </div>
        <div className="nav-links">
          <span className={`nav-link ${activeTab === 'Dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('Dashboard')}>Dashboard</span>
          <span className={`nav-link ${activeTab === 'Analytics' ? 'active' : ''}`} onClick={() => setActiveTab('Analytics')}>Analytics</span>
          <span className={`nav-link ${activeTab === 'ML Models' ? 'active' : ''}`} onClick={() => setActiveTab('ML Models')}>ML Models</span>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="hero">
        <div className="hero-badge">
          <Leaf size={14} />
          <span>Enterprise Analytics Platform</span>
        </div>
        <h1>Global Climate &<br/><span className="gradient-text">Wellbeing Analytics</span></h1>
        <p className="hero-sub">Real-time insights powered by DuckDB, Machine Learning & Gemini AI</p>
      </header>

      {/* Dashboard Tab */}
      {activeTab === 'Dashboard' && (
        <>
          {summary && summary.status !== "empty" && (
            <section className="metrics-row">
              <div className="metric-card">
                <div className="metric-icon" style={{background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8'}}>
                  <Globe size={22} />
                </div>
                <div className="metric-info">
                  <span className="metric-label">Countries Analyzed</span>
                  <span className="metric-value">{summary.countries_count}</span>
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-icon" style={{background: 'rgba(244, 114, 182, 0.15)', color: '#f472b6'}}>
                  <HeartPulse size={22} />
                </div>
                <div className="metric-info">
                  <span className="metric-label">Avg Happiness</span>
                  <span className="metric-value">{summary.avg_happiness}</span>
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-icon" style={{background: 'rgba(52, 211, 153, 0.15)', color: '#34d399'}}>
                  <TrendingUp size={22} />
                </div>
                <div className="metric-info">
                  <span className="metric-label">Avg GDP</span>
                  <span className="metric-value">${summary.avg_gdp?.toLocaleString()}</span>
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-icon" style={{background: 'rgba(251, 191, 36, 0.15)', color: '#fbbf24'}}>
                  <Activity size={22} />
                </div>
                <div className="metric-info">
                  <span className="metric-label">Avg CO₂</span>
                  <span className="metric-value">{summary.avg_co2}</span>
                </div>
              </div>
            </section>
          )}

          <section className="charts-section">
            <div className="chart-card">
              <div className="chart-header">
                <h2>Top 10 Happiest Countries</h2>
                <span className="chart-badge">Bar Chart</span>
              </div>
              <div className="chart-body">
                <ResponsiveContainer width="100%" height={340}>
                  <BarChart data={chartData.top10} layout="vertical" margin={{ top: 5, right: 30, left: 5, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.04)" />
                    <XAxis type="number" hide />
                    <YAxis dataKey="country_name" type="category" width={110} tick={{fill: '#64748b', fontSize: 13}} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="happiness_score" radius={[0, 8, 8, 0]} fill="url(#barGradient)" />
                    <defs>
                      <linearGradient id="barGradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#6366f1" />
                        <stop offset="100%" stopColor="#a78bfa" />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <h2>GDP vs Happiness</h2>
                <span className="chart-badge">Scatter Plot</span>
              </div>
              <div className="chart-body">
                <ResponsiveContainer width="100%" height={340}>
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.04)" />
                    <XAxis type="number" dataKey="gdp_per_capita" name="GDP" tick={{fill: '#64748b', fontSize: 12}} stroke="rgba(0,0,0,0.08)" />
                    <YAxis type="number" dataKey="happiness_score" name="Happiness" tick={{fill: '#64748b', fontSize: 12}} stroke="rgba(0,0,0,0.08)" />
                    <ZAxis type="category" dataKey="country_name" name="Country" />
                    <Tooltip cursor={{strokeDasharray: '3 3'}} content={<CustomTooltip />} />
                    <Scatter name="Countries" data={chartData.scatter} fill="#34d399" opacity={0.7} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>
        </>
      )}

      {/* Analytics Tab */}
      {activeTab === 'Analytics' && (
        <section className="charts-section">
          <div className="chart-card">
            <div className="chart-header">
              <h2>Bottom 10 Happiest Countries</h2>
              <span className="chart-badge">Bar Chart</span>
            </div>
            <div className="chart-body">
              <ResponsiveContainer width="100%" height={340}>
                <BarChart data={chartData.bottom10} layout="vertical" margin={{ top: 5, right: 30, left: 5, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.04)" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="country_name" type="category" width={110} tick={{fill: '#64748b', fontSize: 13}} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="happiness_score" radius={[0, 8, 8, 0]} fill="#f472b6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card">
            <div className="chart-header">
              <h2>Life Expectancy vs Happiness</h2>
              <span className="chart-badge">Scatter Plot</span>
            </div>
            <div className="chart-body">
              <ResponsiveContainer width="100%" height={340}>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.04)" />
                  <XAxis type="number" dataKey="life_expectancy" name="Life Expectancy" tick={{fill: '#64748b', fontSize: 12}} stroke="rgba(0,0,0,0.08)" />
                  <YAxis type="number" dataKey="happiness_score" name="Happiness" tick={{fill: '#64748b', fontSize: 12}} stroke="rgba(0,0,0,0.08)" />
                  <ZAxis type="category" dataKey="country_name" name="Country" />
                  <Tooltip cursor={{strokeDasharray: '3 3'}} content={<CustomTooltip />} />
                  <Scatter name="Countries" data={chartData.lifeExp} fill="#6366f1" opacity={0.7} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card">
            <div className="chart-header">
              <h2>Social Support vs Happiness</h2>
              <span className="chart-badge">Scatter Plot</span>
            </div>
            <div className="chart-body">
              <ResponsiveContainer width="100%" height={340}>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.04)" />
                  <XAxis type="number" dataKey="social_support" name="Social Support" tick={{fill: '#64748b', fontSize: 12}} stroke="rgba(0,0,0,0.08)" />
                  <YAxis type="number" dataKey="happiness_score" name="Happiness" tick={{fill: '#64748b', fontSize: 12}} stroke="rgba(0,0,0,0.08)" />
                  <ZAxis type="category" dataKey="country_name" name="Country" />
                  <Tooltip cursor={{strokeDasharray: '3 3'}} content={<CustomTooltip />} />
                  <Scatter name="Countries" data={chartData.social} fill="#fbbf24" opacity={0.7} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>
      )}

      {/* ML Models Tab */}
      {activeTab === 'ML Models' && (
        <section className="predictor-section">
          <div className="predictor-card">
            <div className="predictor-header">
              <Brain size={24} />
              <div>
                <h2>Happiness Predictor</h2>
                <p>Random Forest ML model trained on global wellbeing data</p>
              </div>
            </div>
            
            <div className="predictor-grid">
              <div className="field-group">
                <label>GDP per Capita ($)</label>
                <input type="number" value={features.gdp_per_capita} onChange={e => setFeatures({...features, gdp_per_capita: parseFloat(e.target.value)})} />
              </div>
              <div className="field-group">
                <label>Social Support</label>
                <input type="number" step="0.1" value={features.social_support} onChange={e => setFeatures({...features, social_support: parseFloat(e.target.value)})} />
              </div>
              <div className="field-group">
                <label>Life Expectancy</label>
                <input type="number" step="0.1" value={features.life_expectancy} onChange={e => setFeatures({...features, life_expectancy: parseFloat(e.target.value)})} />
              </div>
              <div className="field-group">
                <label>Freedom</label>
                <input type="number" step="0.1" value={features.freedom} onChange={e => setFeatures({...features, freedom: parseFloat(e.target.value)})} />
              </div>
              <div className="field-group">
                <label>Corruption</label>
                <input type="number" step="0.01" value={features.corruption} onChange={e => setFeatures({...features, corruption: parseFloat(e.target.value)})} />
              </div>
            </div>

            <button className="predict-btn" onClick={handlePredict} disabled={predictLoading}>
              {predictLoading ? (
                <><span className="spinner" /> Calculating...</>
              ) : (
                <><Sparkles size={18} /> Run Prediction</>
              )}
            </button>

            {prediction !== null && (
              <div className="prediction-result">
                <span className="result-label">Predicted Happiness Score</span>
                <span className="result-score">{prediction.toFixed(2)}</span>
                <span className="result-max">/ 10</span>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Floating AI Chat Button */}
      <div className="fab-container">
        {!chatOpen && (
          <div className="fab-tooltip">
            AI asistanınız burda 👋
          </div>
        )}
        <button className="chat-fab" onClick={() => setChatOpen(!chatOpen)} aria-label="Open AI Chat">
          {chatOpen ? <X size={24} /> : <MessageCircle size={24} />}
        </button>
      </div>

      {/* AI Chat Panel (overlay) */}
      {chatOpen && (
        <div className="chat-panel">
          <div className="chat-panel-header">
            <div className="chat-panel-title">
              <Sparkles size={18} />
              <span>AI Data Assistant</span>
            </div>
            <button className="chat-close" onClick={() => setChatOpen(false)}>
              <X size={18} />
            </button>
          </div>
          
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-empty">
                <MessageCircle size={36} />
                <p>Ask anything about the dataset.<br/>e.g. "En mutlu ülke hangisi?"</p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.role}`}>
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            ))}
            {chatLoading && (
              <div className="chat-bubble ai">
                <div className="typing-dots"><span/><span/><span/></div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          
          <div className="chat-input-bar">
            <input 
              type="text"
              placeholder="Ask about the data..."
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleChat()}
            />
            <button onClick={handleChat} disabled={chatLoading || !prompt.trim()}>
              <Send size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
