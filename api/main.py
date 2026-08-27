import os
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator
import duckdb
from google import genai
from dotenv import load_dotenv
import redis
import json
import hashlib

load_dotenv()

# Setup Redis
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# Setup the FastAPI app
app = FastAPI(
    title="Global Happiness Prediction API",
    description="Predicts a country's Happiness Score and handles data requests.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument the app to expose /metrics for Prometheus
Instrumentator().instrument(app).expose(app)

# --- Schemas ---
class HappinessFeatures(BaseModel):
    gdp_per_capita: float
    social_support: float
    life_expectancy: float
    freedom: float
    corruption: float

    class Config:
        json_schema_extra = {
            "example": {
                "gdp_per_capita": 45000.0,
                "social_support": 1.45,
                "life_expectancy": 0.85,
                "freedom": 0.65,
                "corruption": 0.15,
            }
        }

class ChatRequest(BaseModel):
    prompt: string

# Global variables
rf_model = None
project_root = Path(__file__).parent.parent
db_path = project_root / "data" / "climate_wellbeing.duckdb"

@app.on_event("startup")
def load_model():
    """Load the machine learning model when the API starts."""
    global rf_model
    model_path = project_root / "models" / "rf_model.pkl"

    if model_path.exists():
        rf_model = joblib.load(model_path)

@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Happiness Prediction API is running!", "docs_url": "/docs"}

@app.post("/predict")
def predict_happiness(features: HappinessFeatures):
    if rf_model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    try:
        input_df = pd.DataFrame([features.dict()])
        prediction = rf_model.predict(input_df)[0]
        return {
            "predicted_happiness_score": round(float(prediction), 3),
            "features_used": features.dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/summary")
def get_data_summary():
    """Returns basic metrics from DuckDB for the frontend, cached via Redis."""
    cache_key = "data_summary"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass # Ignore redis connection errors during local dev

    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database not found.")
    
    try:
        conn = duckdb.connect(str(db_path), read_only=True)
        df = conn.execute("SELECT * FROM main_marts.fct_climate_economy").df()
        conn.close()
        
        if df.empty:
            return {"status": "empty"}
            
        recent_year = df["year"].max()
        filtered_df = df[df["year"] == recent_year]
        
        result = {
            "year": int(recent_year),
            "avg_happiness": round(filtered_df["happiness_score"].mean(), 2),
            "avg_gdp": round(filtered_df["gdp_per_capita"].mean(), 2),
            "avg_co2": round(filtered_df["co2_per_capita"].mean(), 2),
            "countries_count": len(filtered_df["country_name"].unique())
        }
        
        try:
            redis_client.setex(cache_key, 3600, json.dumps(result)) # Cache for 1 hour
        except Exception:
            pass
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat_with_data(request: ChatRequest):
    """Answers questions using Gemini and DuckDB."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        raise HTTPException(status_code=500, detail="Gemini API Key is missing.")
        
    try:
        client = genai.Client(api_key=gemini_key)
        
        schema_info = "Table: main_marts.fct_climate_economy\nColumns: country_name, year, happiness_score, gdp_per_capita, social_support, life_expectancy, freedom, corruption, co2_per_capita"
        prompt_sql = f"You are a Data Analyst. Based on this DuckDB schema:\n{schema_info}\n\nWrite ONLY a valid DuckDB SQL query to answer this user question: '{request.prompt}'. Do not include markdown formatting like ```sql, just the raw query."
        
        response_sql = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_sql,
        )
        sql_query = response_sql.text.strip().replace("```sql", "").replace("```", "").strip()
        
        conn = duckdb.connect(str(db_path), read_only=True)
        result_df = conn.execute(sql_query).df()
        conn.close()
        
        prompt_nl = f"The user asked: '{request.prompt}'.\nThe database returned this data:\n{result_df.to_string()}\n\nExplain this data to the user in a friendly, concise, and helpful way."
        response_nl = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_nl,
        )
        
        return {
            "answer": response_nl.text,
            "sql_query": sql_query,
            "data": result_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
