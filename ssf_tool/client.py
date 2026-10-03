"""
HTTP Client to interact with the public Simple Stock Flow API.
Does not touch the database directly (Task T-24).
"""

from typing import Any, Dict, List, Optional
import requests


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username: str, password: str) -> str:
        url = f"{self.base_url}/api/auth/login"
        resp = self.session.post(
            url,
            json={"username": username, "password": password},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=10,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Authentication failed ({resp.status_code}): {resp.text}")

        data = resp.json()
        self.token = data.get("accessToken")
        if not self.token:
            raise RuntimeError("Login response missing 'accessToken'")
        return self.token

    def get_categories(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/api/categories"
        resp = self.session.get(url, headers=self._headers(), timeout=10)
        if resp.status_code != 200:
            raise RuntimeError(f"Error fetching categories ({resp.status_code}): {resp.text}")
        return resp.json()

    def get_products(self, search: Optional[str] = None, page: int = 1, size: int = 100) -> Dict[str, Any]:
        url = f"{self.base_url}/api/products"
        params = {"page": page, "size": size}
        if search:
            params["search"] = search
        resp = self.session.get(url, params=params, headers=self._headers(), timeout=10)
        if resp.status_code != 200:
            raise RuntimeError(f"Error listing products ({resp.status_code}): {resp.text}")
        return resp.json()

    def create_product(self, name: str, price: float, stock: int, category_id: str) -> str:
        url = f"{self.base_url}/api/products"
        payload = {
            "name": name,
            "price": price,
            "stock": stock,
            "categoryId": category_id,
        }
        resp = self.session.post(
            url,
            json=payload,
            headers={**self._headers(), "Content-Type": "application/json"},
            timeout=10,
        )
        if resp.status_code != 201:
            raise RuntimeError(f"Error creating product '{name}' ({resp.status_code}): {resp.text}")
        return resp.json().get("id")

    def upload_image(self, product_id: str, file_path: str) -> str:
        url = f"{self.base_url}/api/products/{product_id}/image"
        mime = "image/jpeg" if file_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1].split("\\")[-1], f, mime)}
            resp = self.session.post(
                url,
                files=files,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=15,
            )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Error uploading image for product {product_id} ({resp.status_code}): {resp.text}")
        return resp.json().get("url", "")

    def create_sale(self, lines: List[Dict[str, Any]]) -> str:
        url = f"{self.base_url}/api/sales"
        resp = self.session.post(
            url,
            json={"lines": lines},
            headers={**self._headers(), "Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code != 201:
            raise RuntimeError(f"Error registering sale ({resp.status_code}): {resp.text}")
        return resp.json().get("id")