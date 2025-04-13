import requests
from typing import Any, List, Dict, Optional

class Overseerr:
    def __init__(
            self, 
            api_key: str,
            url: str,
            timeout: tuple = (3, 30)
        ):
        self.api_key = api_key
        self.url = url
        self.timeout = timeout

    def _get_headers(self) -> dict:
        headers = {
            'Accept': 'application/json',
            'X-Api-Key': self.api_key
        }
        return headers

    def _safe_call(self, call_fn):
        try:
            return call_fn()
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.content else {}
            message = error_data.get('message', '<unknown>')
            raise Exception(f"HTTP Error {e.response.status_code}: {message}")
        except requests.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """Get the status of the Overseerr server."""
        url = f"{self.url}/api/v1/status"
        
        def call_fn():
            response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Get movie details for a specific movie ID."""
        url = f"{self.url}/api/v1/movie/{movie_id}"
        
        def call_fn():
            response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_tv_details(self, tv_id: int) -> Dict[str, Any]:
        """Get TV details for a specific TV ID."""
        url = f"{self.url}/api/v1/tv/{tv_id}"
        
        def call_fn():
            response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_season_details(self, tv_id: int, season_id: int) -> Dict[str, Any]:
        """Get season details including episodes for a specific TV show and season."""
        url = f"{self.url}/api/v1/tv/{tv_id}/season/{season_id}"
        
        def call_fn():
            response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def get_requests(self, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Get requests from the Overseerr API."""
        url = f"{self.url}/api/v1/request"
        
        # Build query string
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        if query_string:
            url = f"{url}?{query_string}"
        
        def call_fn():
            response = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)