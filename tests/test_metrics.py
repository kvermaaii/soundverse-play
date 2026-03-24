class TestMetricsEndpoint:
    def test_metrics_endpoint_returns_200(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_no_auth_required(self, client):
        # /metrics should be accessible without API key
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
