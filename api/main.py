import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from prometheus_fastapi_instrumentator import Instrumentator

# Setup the FastAPI app
app = FastAPI(
    title="Global Happiness Prediction API",
    description="Predicts a country's Happiness Score based on socio-economic metrics using a trained Random Forest model.",
    version="1.0.0",
)

# Instrument the app to expose /metrics for Prometheus
Instrumentator().instrument(app).expose(app)


# Define the input schema
class HappinessFeatures(BaseModel):
    gdp_per_capita: float
    social_support: float
    life_expectancy: float
    freedom: float
    corruption: float

    class Config:
        schema_extra = {
            "example": {
                "gdp_per_capita": 45000.0,
                "social_support": 1.45,
                "life_expectancy": 0.85,
                "freedom": 0.65,
                "corruption": 0.15,
            }
        }


# Global variable for the model
rf_model = None


@app.on_event("startup")
def load_model():
    """Load the machine learning model when the API starts."""
    global rf_model
    model_path = Path(__file__).parent.parent / "models" / "rf_model.pkl"

    if not model_path.exists():
        raise RuntimeError(
            f"Model file not found at {model_path}. Please run generate_images.py first."
        )

    rf_model = joblib.load(model_path)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Happiness Prediction API is running!", "docs_url": "/docs"}


@app.post("/predict")
def predict_happiness(features: HappinessFeatures):
    """
    Predict the Happiness Score for a given set of features.
    """
    if rf_model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    try:
        # Convert input to DataFrame (to match feature names used during training)
        input_df = pd.DataFrame([features.dict()])

        # Make prediction
        prediction = rf_model.predict(input_df)[0]

        return {
            "predicted_happiness_score": round(float(prediction), 3),
            "features_used": features.dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
