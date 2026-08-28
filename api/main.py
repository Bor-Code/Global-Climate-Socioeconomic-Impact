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
from kafka import KafkaProducer
import threading

load_dotenv()

# Setup Redis
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# Setup Kafka Producer (lazy initialization to avoid crash if kafka is down)
kafka_producer = None
def get_kafka_producer():
    global kafka_producer
    if kafka_producer is None:
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=['kafka:29092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception:
            pass
    return kafka_producer

# Setup the FastAPI app
app = FastAPI(
    title="Global Happiness Prediction API",
    description="Predicts a country's Happiness Score and handles data requests.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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
    prompt: str

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
        
        result = {
            "predicted_happiness_score": round(float(prediction), 3),
            "features_used": features.dict(),
        }
        
        # Publish to Kafka in background thread (non-blocking)
        def publish_kafka():
            try:
                producer = get_kafka_producer()
                if producer:
                    producer.send('prediction_events', result)
            except Exception:
                pass
        threading.Thread(target=publish_kafka, daemon=True).start()
                
        return result
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

@app.get("/api/data/charts")
def get_chart_data():
    """Returns structured data for frontend Recharts visualization."""
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database not found.")
    
    try:
        conn = duckdb.connect(str(db_path), read_only=True)
        # Top 10 Happiest Countries for Bar Chart
        top_10_df = conn.execute("SELECT country_name, happiness_score FROM main_marts.fct_climate_economy WHERE year = (SELECT MAX(year) FROM main_marts.fct_climate_economy) ORDER BY happiness_score DESC LIMIT 10").df()
        
        # Bottom 10 Happiest
        bottom_10_df = conn.execute("SELECT country_name, happiness_score FROM main_marts.fct_climate_economy WHERE year = (SELECT MAX(year) FROM main_marts.fct_climate_economy) AND happiness_score IS NOT NULL ORDER BY happiness_score ASC LIMIT 10").df()

        # GDP vs Happiness for Scatter Plot
        scatter_df = conn.execute("SELECT country_name, gdp_per_capita, happiness_score FROM main_marts.fct_climate_economy WHERE year = (SELECT MAX(year) FROM main_marts.fct_climate_economy) AND gdp_per_capita IS NOT NULL AND happiness_score IS NOT NULL").df()

        # Life Expectancy vs Happiness
        life_exp_df = conn.execute("SELECT country_name, life_expectancy, happiness_score FROM main_marts.fct_climate_economy WHERE year = (SELECT MAX(year) FROM main_marts.fct_climate_economy) AND life_expectancy IS NOT NULL AND happiness_score IS NOT NULL").df()
        
        # Social Support vs Happiness
        social_df = conn.execute("SELECT country_name, social_support, happiness_score FROM main_marts.fct_climate_economy WHERE year = (SELECT MAX(year) FROM main_marts.fct_climate_economy) AND social_support IS NOT NULL AND happiness_score IS NOT NULL").df()

        conn.close()
        
        return {
            "top10": top_10_df.to_dict(orient="records"),
            "bottom10": bottom_10_df.to_dict(orient="records"),
            "scatter": scatter_df.to_dict(orient="records"),
            "lifeExp": life_exp_df.to_dict(orient="records"),
            "social": social_df.to_dict(orient="records")
        }
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
        
        prompt_sql = f"""You are a Data Analyst assistant for a database with this schema:
{schema_info}

The user asked: '{request.prompt}'

If this question requires querying the database, return ONLY the raw DuckDB SQL query (no markdown, no ```sql).
If this is a greeting or general chit-chat (like 'merhaba', 'hello', 'who are you'), reply with NO_SQL followed by your conversational response. For example: 'NO_SQL: Merhaba! Size iklim, ekonomi ve mutluluk verileri konusunda nasıl yardımcı olabilirim?'"""
        
        response_sql = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt_sql,
        )
        raw_text = response_sql.text.strip()
        
        if raw_text.startswith("NO_SQL"):
            answer = raw_text.replace("NO_SQL:", "").replace("NO_SQL", "").strip()
            return {
                "answer": answer,
                "sql_query": None,
                "data": []
            }
            
        sql_query = raw_text.replace("```sql", "").replace("```", "").strip()
        
        try:
            conn = duckdb.connect(str(db_path), read_only=True)
            result_df = conn.execute(sql_query).df()
            conn.close()
            
            prompt_nl = f"The user asked: '{request.prompt}'.\nThe database returned this data:\n{result_df.to_string()}\n\nExplain this data to the user in a friendly, concise, and helpful way in the same language they asked."
            response_nl = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_nl,
            )
            
            return {
                "answer": response_nl.text,
                "sql_query": sql_query,
                "data": result_df.to_dict(orient="records")
            }
        except Exception as sql_err:
            # Fallback to direct conversational answer if SQL execution fails
            prompt_general = f"The user asked: '{request.prompt}'. Answer their question or greeting politely and inform them you can analyze the climate and happiness database for them."
            response_general = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt_general,
            )
            return {
                "answer": response_general.text,
                "sql_query": None,
                "data": []
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        err_msg = str(e)
        if "503" in err_msg or "UNAVAILABLE" in err_msg:
            return {
                "answer": "Yapay zeka servisi şu an yoğun talep nedeniyle geçici olarak meşgul. Lütfen birkaç saniye sonra sorunuzu tekrar deneyin.",
                "sql_query": None,
                "data": []
            }
        return {
            "answer": f"Bir hata oluştu: {err_msg[:100]}... Lütfen tekrar deneyin.",
            "sql_query": None,
            "data": []
        }
