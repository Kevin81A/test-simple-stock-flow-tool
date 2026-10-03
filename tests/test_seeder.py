"""
Pruebas unitarias para el sembrador de datos (T-24).
Verifica que las peticiones se realicen a la API simulada sin tocar base de datos.
"""

import unittest
from unittest.mock import MagicMock, patch
from ssf_tool.client import ApiClient
from ssf_tool.seeder import run_seed


class TestSeeder(unittest.TestCase):
    @patch("ssf_tool.client.requests.Session")
    def test_client_login_success(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"accessToken": "fake-jwt-token"}
        mock_session.post.return_value = mock_resp

        client = ApiClient("http://localhost:8000")
        token = client.login("admin", "Admin12345!")

        self.assertEqual(token, "fake-jwt-token")
        self.assertEqual(client.token, "fake-jwt-token")

    @patch("ssf_tool.client.requests.Session")
    def test_client_create_product(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"id": "prod-uuid-123"}
        mock_session.post.return_value = mock_resp

        client = ApiClient("http://localhost:8000")
        client.token = "fake-jwt"
        prod_id = client.create_product("Café", 15000.0, 10, "cat-uuid")

        self.assertEqual(prod_id, "prod-uuid-123")


if __name__ == "__main__":
    unittest.main()
