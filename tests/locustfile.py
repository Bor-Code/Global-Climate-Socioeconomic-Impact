from locust import HttpUser, task, between

class APIUser(HttpUser):
    # Simulate a user waiting between 1 and 3 seconds between actions
    wait_time = between(1, 3)

    @task(3)
    def test_get_summary(self):
        """Simulate loading the frontend dashboard (hits /api/data/summary)"""
        self.client.get("/api/data/summary")

    @task(1)
    def test_predict(self):
        """Simulate a user making an ML prediction"""
        payload = {
            "gdp_per_capita": 45000.0,
            "social_support": 1.45,
            "life_expectancy": 0.85,
            "freedom": 0.65,
            "corruption": 0.15
        }
        self.client.post("/predict", json=payload)
