"""HTTP client for MISP API interactions."""

import asyncio
import csv
import io
import httpx
from typing import Any, Dict, List, Optional
from misp_cli.core.config import MISPProfile
from misp_cli.core.exceptions import (
    MISPAPIError,
    MISPConnectionError,
    MISPAuthenticationError,
    MISPNotFoundError,
    MISPRateLimitError,
)


class MISPCLient:
    """
    Async HTTP client for MISP API interactions.

    Handles authentication, request formatting, and response processing.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        verify_ssl: bool = True,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def headers(self) -> Dict[str, str]:
        """Get common headers for API requests."""
        return {
            "Authorization": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                verify=self.verify_ssl,
                timeout=self.timeout,
                headers=self.headers,
            )
        return self._client

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an API request to MISP.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data

        Returns:
            API response as dictionary

        Raises:
            MISPAPIError: On API error responses
            MISPConnectionError: On connection failures
        """
        client = await self.get_client()
        url = f"{self.base_url}{endpoint}"

        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=data,
            )
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise MISPConnectionError(f"Connection failed: {e}")
        except httpx.TimeoutException as e:
            raise MISPConnectionError(f"Request timed out: {e}")
        except httpx.HTTPError as e:
            raise MISPConnectionError(f"HTTP error: {e}")

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """GET request helper."""
        return await self.request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """POST request helper."""
        return await self.request("POST", endpoint, data=data)

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """PUT request helper."""
        return await self.request("PUT", endpoint, data=data)

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """DELETE request helper."""
        return await self.request("DELETE", endpoint, params=params)

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Process API response."""
        try:
            response_data = response.json()
        except Exception:
            response_data = {"raw_response": response.text}

        # Handle error status codes
        if response.status_code >= 400:
            error_type = response_data.get("name", "API Error")
            message = response_data.get("message", response_data.get("error", f"HTTP {response.status_code}"))

            # Avoid duplicating the error message if name and message are the same
            if error_type == message:
                message = response_data.get("error", message)

            if response.status_code == 401:
                raise MISPAuthenticationError(message, status_code=401, error_type=error_type)
            elif response.status_code == 403:
                raise MISPAuthenticationError(message, status_code=403, error_type=error_type)
            elif response.status_code == 404:
                raise MISPNotFoundError("Resource", response.url.path, response_body=response.text)
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", 60)
                raise MISPRateLimitError(message, retry_after=int(retry_after))
            else:
                raise MISPAPIError(
                    message,
                    status_code=response.status_code,
                    response_body=response.text,
                    error_type=error_type,
                )

        # Return response data
        if isinstance(response_data, dict):
            return response_data
        return {"data": response_data}

    @classmethod
    def from_profile(cls, profile: MISPProfile) -> "MISPCLient":
        """Create client from MISPProfile configuration."""
        return cls(
            base_url=profile.url,
            api_key=profile.api_key,
            verify_ssl=profile.verify_ssl,
            timeout=profile.timeout,
        )

    # Output formatting methods
    @staticmethod
    def format_as_csv(data: List[Dict], columns: Optional[List[str]] = None) -> str:
        """
        Format data as CSV.
        
        Args:
            data: List of dictionaries to format
            columns: Optional list of columns to include (in order)
        
        Returns:
            CSV formatted string
        """
        if not data:
            return ""
        
        # Determine columns to use
        if columns:
            keys = columns
        else:
            keys = list(data[0].keys()) if data else []
        
        # Handle None values
        def clean_value(value: Any) -> str:
            if value is None:
                return ""
            elif isinstance(value, (dict, list)):
                return str(len(value))
            return str(value)
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for row in data:
            cleaned_row = {k: clean_value(v) for k, v in row.items() if k in keys}
            writer.writerow(cleaned_row)
        
        return output.getvalue()

    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(MISPCLient.flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    # Synchronous wrapper methods for CLI usage
    def get_sync(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronous GET request helper."""
        return asyncio.run(self.get(endpoint, params=params))

    def post_sync(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronous POST request helper."""
        return asyncio.run(self.post(endpoint, data=data))

    def put_sync(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronous PUT request helper."""
        return asyncio.run(self.put(endpoint, data=data))

    def delete_sync(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronous DELETE request helper."""
        return asyncio.run(self.delete(endpoint, params=params))

    def close_sync(self):
        """Synchronous close helper."""
        if self._client and not self._client.is_closed:
            asyncio.run(self._client.aclose())
