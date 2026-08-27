import pytest
from fastapi.testclient import TestClient
from api.main import app

def test_read_root():
    """Test the root endpoint."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Happiness Prediction API is running!", "docs_url": "/docs"}

def test_predict_happy_path():
    """Test the /predict endpoint with valid data."""
    payload = {
        "gdp_per_capita": 45000.0,
        "social_support": 1.45,
        "life_expectancy": 0.85,
        "freedom": 0.65,
        "corruption": 0.15
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check if prediction exists and is a float
        assert "predicted_happiness_score" in data
        assert isinstance(data["predicted_happiness_score"], float)
        
        # Happiness scores usually fall between 0 and 10
        assert 0.0 <= data["predicted_happiness_score"] <= 10.0
        
        # Check if inputs are echoed back correctly
        assert data["features_used"] == payload

def test_predict_error_path_missing_fields():
    """Test the /predict endpoint with missing required fields."""
    payload = {
        "gdp_per_capita": 45000.0,
        # Missing social_support
        "life_expectancy": 0.85,
        "freedom": 0.65,
        "corruption": 0.15
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        
        # FastAPI should automatically return 422 Unprocessable Entity for missing fields
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # Ensure the error message mentions the missing field 'social_support'
        error_msg = str(data["detail"])
        assert "social_support" in error_msg

def test_predict_error_path_invalid_types():
    """Test the /predict endpoint with invalid data types."""
    payload = {
        "gdp_per_capita": "Not a number",
        "social_support": 1.45,
        "life_expectancy": 0.85,
        "freedom": 0.65,
        "corruption": 0.15
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        
        # FastAPI should automatically return 422 Unprocessable Entity for invalid types
        assert response.status_code == 422
