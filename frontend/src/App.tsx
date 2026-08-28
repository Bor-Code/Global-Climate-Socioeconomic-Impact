import { useState, useEffect } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { Send, Activity, Globe, HeartPulse } from 'lucide-react'
import './App.css'

const API_URL = "http://localhost:8000"

function App() {
  const [summary, setSummary] = useState<any>(null)
  
  // Predictor State
  const [features, setFeatures] = useState({
    gdp_per_capita: 45000.0,
    social_support: 1.45,
    life_expectancy: 0.85,
    freedom: 0.65,
    corruption: 0.15
  })
  const [prediction, setPrediction] = useState<number | null>(null)
  
  // Chat State
  const [messages, setMessages] = useState<any[]>([])
  const [prompt, setPrompt] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Fetch summary on load
    axios.get(`${API_URL}/api/data/summary`)
      .then(res => setSummary(res.data))
      .catch(err => console.error("Could not load summary", err))
  }, [])

  const [predictLoading, setPredictLoading] = useState(false)

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
      alert("Error predicting score. Check backend logs.")
    } finally {
      setPredictLoading(false)
    }
  }

  const handleChat = async () => {
    if (!prompt.trim()) return
    
    const newMessages = [...messages, { role: 'user', content: prompt }]
    setMessages(newMessages)
    setPrompt("")
    setLoading(true)
    
    try {
      const res = await axios.post(`${API_URL}/api/chat`, { prompt })
      setMessages([...newMessages, { role: 'ai', content: res.data.answer }])
    } catch (err) {
      console.error(err)
      setMessages([...newMessages, { role: 'ai', content: "Sorry, I encountered an error. Check your API key or backend logs." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>Global Climate & Wellbeing Analytics</h1>
        <p>Advanced Enterprise Dashboard built with React, FastAPI, DuckDB & Gemini</p>
      </header>

      {summary && summary.status !== "empty" && (
        <div className="glass-panel metric-grid">
          <div className="metric-card">
            <h3><Globe size={18} style={{marginRight: '8px'}}/>Countries</h3>
            <p>{summary.countries_count}</p>
          </div>
          <div className="metric-card">
            <h3><HeartPulse size={18} style={{marginRight: '8px'}}/>Avg Happiness</h3>
            <p>{summary.avg_happiness}</p>
          </div>
          <div className="metric-card">
            <h3><Activity size={18} style={{marginRight: '8px'}}/>Avg GDP</h3>
            <p>${summary.avg_gdp}</p>
          </div>
          <div className="metric-card">
            <h3>☁️ Avg CO2</h3>
            <p>{summary.avg_co2}</p>
          </div>
        </div>
      )}

      <div className="grid-container">
        {/* Predictor Panel */}
        <div className="glass-panel">
          <h2>Predict Happiness Score</h2>
          <p style={{color: '#8b949e', marginBottom: '1.5rem'}}>Use our Random Forest ML Model to predict a country's wellbeing.</p>
          
          <label>GDP per Capita</label>
          <input type="number" className="input-field" 
                 value={features.gdp_per_capita} 
                 onChange={e => setFeatures({...features, gdp_per_capita: parseFloat(e.target.value)})} />
                 
          <label>Social Support (0-2)</label>
          <input type="number" step="0.1" className="input-field" 
                 value={features.social_support} 
                 onChange={e => setFeatures({...features, social_support: parseFloat(e.target.value)})} />

          <label>Life Expectancy (0-1.5)</label>
          <input type="number" step="0.1" className="input-field" 
                 value={features.life_expectancy} 
                 onChange={e => setFeatures({...features, life_expectancy: parseFloat(e.target.value)})} />

          <button className="btn-primary" onClick={handlePredict} disabled={predictLoading} style={{marginTop: '1rem', opacity: predictLoading ? 0.7 : 1}}>
            {predictLoading ? "Calculating..." : "Run ML Prediction"}
          </button>

          {prediction !== null && (
            <div className="prediction-result">
              <p>Predicted Score</p>
              <h2>{prediction.toFixed(2)} / 10</h2>
            </div>
          )}
        </div>

        {/* AI Chat Panel */}
        <div className="glass-panel">
          <h2>Ask the AI (SQL Agent)</h2>
          <p style={{color: '#8b949e', marginBottom: '1rem'}}>Chat directly with our DuckDB data warehouse via Gemini.</p>
          
          <div className="chat-container">
            <div className="chat-history">
              {messages.length === 0 && <p style={{color: '#8b949e', textAlign: 'center'}}>Ask something like: "Which country has the highest GDP?"</p>}
              {messages.map((m, idx) => (
                <div key={idx} className={`chat-message ${m.role}`}>
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              ))}
              {loading && <div className="chat-message ai"><p>Thinking...</p></div>}
            </div>
            
            <div className="chat-input-wrapper">
              <input 
                type="text" 
                className="input-field" 
                placeholder="Ask about the data..." 
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleChat()}
              />
              <button className="btn-primary" style={{width: 'auto', padding: '10px 20px'}} onClick={handleChat}>
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
