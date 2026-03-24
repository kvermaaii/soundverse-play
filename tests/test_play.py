from unittest.mock import MagicMock, patch


class TestListClips:
    def test_list_clips_empty(self, client, api_headers):
        response = client.get("/play", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["clips"] == []
        assert data["count"] == 0

    def test_list_clips_returns_seeded_data(self, client, api_headers, seed_clips):
        response = client.get("/play", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert data["clips"][0]["title"] == "Test Ambient"

    def test_list_clips_requires_api_key(self, client):
        response = client.get("/play")
        assert response.status_code == 422  # missing header

    def test_list_clips_rejects_invalid_api_key(self, client):
        response = client.get("/play", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 401


class TestStreamClip:
    def test_stream_increments_play_count(
        self, client, api_headers, seed_clips, db_session
    ):
        clip_id = seed_clips[0].id
        # Mock httpx.Client to avoid real HTTP calls
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.iter_bytes = MagicMock(return_value=iter([b"fake-audio-data"]))
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_response)
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)

        with patch("app.services.clip_service.httpx.Client", return_value=mock_client):
            response = client.get(f"/play/{clip_id}/stream", headers=api_headers)
            assert response.status_code == 200

        db_session.refresh(seed_clips[0])
        assert seed_clips[0].play_count == 1

    def test_stream_nonexistent_returns_404(self, client, api_headers):
        response = client.get("/play/999/stream", headers=api_headers)
        assert response.status_code == 404

    def test_stream_returns_audio_content_type(self, client, api_headers, seed_clips):
        clip_id = seed_clips[0].id
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.iter_bytes = MagicMock(return_value=iter([b"fake-audio"]))
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_response)
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)

        with patch("app.services.clip_service.httpx.Client", return_value=mock_client):
            response = client.get(f"/play/{clip_id}/stream", headers=api_headers)
            assert response.headers["content-type"] == "audio/mpeg"


class TestClipStats:
    def test_stats_returns_metadata(self, client, api_headers, seed_clips):
        clip_id = seed_clips[1].id
        response = client.get(f"/play/{clip_id}/stats", headers=api_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Pop"
        assert data["play_count"] == 5
        assert data["genre"] == "pop"

    def test_stats_nonexistent_returns_404(self, client, api_headers):
        response = client.get("/play/999/stats", headers=api_headers)
        assert response.status_code == 404


class TestCreateClip:
    def test_create_clip_success(self, client, api_headers):
        payload = {
            "title": "New Track",
            "description": "A brand new track",
            "genre": "electronic",
            "duration": 45.0,
            "audio_url": "https://example.com/new.mp3",
        }
        response = client.post("/play", json=payload, headers=api_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Track"
        assert data["play_count"] == 0
        assert "id" in data

    def test_create_clip_missing_fields_returns_422(self, client, api_headers):
        payload = {"title": "Incomplete"}
        response = client.post("/play", json=payload, headers=api_headers)
        assert response.status_code == 422
