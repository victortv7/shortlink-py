import os
import httpx
from src.app.base62 import encode, decode


class TestIntegration:
    @classmethod
    def setup_class(cls):
        cls.current_id = 100000000
        cls.APP_HOST = os.getenv("APP_HOST", "test-app")
        cls.APP_PORT = os.getenv("APP_PORT", 8080)
        cls.APP_URL = f"http://{cls.APP_HOST}:{cls.APP_PORT}"

    def test_health(self):
        response = httpx.get(f"{self.APP_URL}/health")
        assert response.status_code == 200

    def test_create_short_link_with_invalid_url(self):
        invalid_url = "htttps//invalid-url"
        response = httpx.post(f"{self.APP_URL}/create", json={"long_url": invalid_url})
        assert response.status_code == 422

    def test_create_short_link(self):
        test_long_url = "https://example.com"
        expected_short_link = encode(self.current_id)

        response = httpx.post(
            f"{self.APP_URL}/create", json={"long_url": test_long_url}
        )
        assert response.status_code == 200
        assert response.json() == {"short_link": expected_short_link}

        TestIntegration.current_id += 1

    def test_create_short_link_and_redirect(self):
        test_long_url = "https://example2.com/"

        create_response = httpx.post(
            f"{self.APP_URL}/create", json={"long_url": test_long_url}
        )
        assert create_response.status_code == 200
        TestIntegration.current_id += 1

        short_link = create_response.json()["short_link"]

        redirect_response = httpx.get(f"{self.APP_URL}/{short_link}")

        assert redirect_response.status_code == 307
        assert redirect_response.headers["Location"] == test_long_url

    def test_get_stats(self):
        test_long_url = "https://example3.com.br/"
        create_response = httpx.post(
            f"{self.APP_URL}/create", json={"long_url": test_long_url}
        )
        assert create_response.status_code == 200
        TestIntegration.current_id += 1

        short_link = create_response.json()["short_link"]
        redirect_response = httpx.get(f"{self.APP_URL}/{short_link}")
        assert redirect_response.status_code == 307
        assert redirect_response.headers["Location"] == test_long_url

        short_link = create_response.json()["short_link"]
        redirect_response = httpx.get(f"{self.APP_URL}/{short_link}")
        assert redirect_response.status_code == 307
        assert redirect_response.headers["Location"] == test_long_url

        stats_response = httpx.get(f"{self.APP_URL}/stats/{short_link}")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["access_count"] == 2

    def test_get_stats_for_nonexistent_short_link(self):
        nonexistent_short_link = encode(self.current_id)
        stats_response = httpx.get(f"{self.APP_URL}/stats/{nonexistent_short_link}")

        assert stats_response.status_code == 404
        assert stats_response.json() == {"detail": "Short link not found"}
