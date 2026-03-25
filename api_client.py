import requests
import json
import os
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CookieAPIClient:
    """
    A comprehensive API client that handles cookie-based authentication
    and provides methods for making authenticated requests.
    """
    
    def __init__(self, cookie_file: str = None, base_url: str = None):
        """
        Initialize the API client with cookie file and base URL.
        
        Args:
            cookie_file (str): Path to the cookie file
            base_url (str): Base URL for the API
        """
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        self.cookie_file = cookie_file or os.getenv("COOKIE_FILE", "cookie.json")
        self.base_url = (base_url or os.getenv("API_BASE_URL", "https://opm.pucrs.br")).rstrip('/')
        self.session = requests.Session()
        self.cookies = self._load_cookies(self.cookie_file)
        self._setup_session()
    
    def _load_cookies(self, cookie_file: str) -> Dict[str, str]:
        """
        Load cookies from specified file.
        
        Args:
            cookie_file (str): Path to cookie file
            
        Returns:
            Dict[str, str]: Dictionary of cookie name-value pairs
        """
        try:
            with open(cookie_file, 'r') as f:
                content = f.read().strip()
            
            # Try to parse as JSON first (new format)
            try:
                cookie_data = json.loads(content)
                cookies = {}
                
                # Handle both array format and object format
                if isinstance(cookie_data, list):
                    # Array of cookie objects
                    for cookie in cookie_data:
                        if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                            cookies[cookie['name']] = cookie['value']
                elif isinstance(cookie_data, dict):
                    # Single cookie object or cookies object
                    if 'cookies' in cookie_data:
                        # Format with "cookies" wrapper
                        for cookie in cookie_data['cookies']:
                            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                                cookies[cookie['name']] = cookie['value']
                    else:
                        # Direct cookie object
                        if 'name' in cookie_data and 'value' in cookie_data:
                            cookies[cookie_data['name']] = cookie_data['value']
                
                return cookies
                
            except json.JSONDecodeError:
                # Fall back to cookie string format (old format)
                cookies = {}
                for cookie in content.split(';'):
                    if '=' in cookie:
                        name, value = cookie.strip().split('=', 1)
                        cookies[name] = value
                return cookies
            
        except FileNotFoundError:
            print(f"Warning: Cookie file '{cookie_file}' not found.")
            return {}
        except Exception as e:
            print(f"Error loading cookies: {e}")
            return {}
    
    def _setup_session(self):
        """Setup the requests session with cookies and headers."""
        # Add cookies to session
        for name, value in self.cookies.items():
            self.session.cookies.set(name, value)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a GET request to the specified endpoint.
        
        Args:
            endpoint (str): API endpoint (relative to base_url)
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            requests.Response: The response object
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making GET request to {url}: {e}")
            raise
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
             json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a POST request to the specified endpoint.
        
        Args:
            endpoint (str): API endpoint (relative to base_url)
            data (Optional[Dict[str, Any]]): Form data
            json_data (Optional[Dict[str, Any]]): JSON data
            
        Returns:
            requests.Response: The response object
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, data=data, json=json_data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making POST request to {url}: {e}")
            raise
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
            json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a PUT request to the specified endpoint.
        
        Args:
            endpoint (str): API endpoint (relative to base_url)
            data (Optional[Dict[str, Any]]): Form data
            json_data (Optional[Dict[str, Any]]): JSON data
            
        Returns:
            requests.Response: The response object
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.put(url, data=data, json=json_data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making PUT request to {url}: {e}")
            raise
    
    def delete(self, endpoint: str) -> requests.Response:
        """
        Make a DELETE request to the specified endpoint.
        
        Args:
            endpoint (str): API endpoint (relative to base_url)
            
        Returns:
            requests.Response: The response object
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making DELETE request to {url}: {e}")
            raise
    
    def get_json(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request and return JSON response.
        
        Args:
            endpoint (str): API endpoint (relative to base_url)
            params (Optional[Dict[str, Any]]): Query parameters
            
        Returns:
            Dict[str, Any]: JSON response as dictionary
        """
        response = self.get(endpoint, params)
        return response.json()
    
    def post_json(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                  json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request and return JSON response.
        
        Args:
            endpoint (str): API endpoint (relative to base_url)
            data (Optional[Dict[str, Any]]): Form data
            json_data (Optional[Dict[str, Any]]): JSON data
            
        Returns:
            Dict[str, Any]: JSON response as dictionary
        """
        response = self.post(endpoint, data, json_data)
        return response.json()
    
    def check_authentication(self, url: str) -> bool:
        """
        Check if the current session is authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            # Try to access a protected endpoint
            response = self.get(url)
            return response.status_code == 200
        except:
            return False
    
    def get_cookies_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded cookies.
        
        Returns:
            Dict[str, Any]: Cookie information
        """
        return {
            "total_cookies": len(self.cookies),
            "cookie_names": list(self.cookies.keys()),
            "session_cookies": dict(self.session.cookies)
        }


def main():
    """Example usage of the CookieAPIClient."""
    
    # Initialize the client
    client = CookieAPIClient()
    
    # Check authentication
    if client.check_authentication():
        print("✅ Authentication successful!")
    else:
        print("❌ Authentication failed!")
        return
    
    # Example: Get correction flow data
    try:
        params = {
            "project_office_id": "11820",
            "period_id": "20076",
            "limit": "20",
            "page": "1",
            "search": "",
            "regularities_ids": "",
            "phase_orders": os.getenv("PHASE_ORDERS", "1"),
            "status_ids": os.getenv("STATUS_IDS", "4"),
            "students_ids": ""
        }
        
        print("\n📊 Fetching correction flow data...")
        response = client.get_json("/api/project-office-v2/correction-flow", params)
        
        print(f"✅ Success! Response status: {response.get('status', 'N/A')}")
        print(f"📄 Response keys: {list(response.keys())}")
        
        # Print some sample data
        if 'data' in response:
            data = response['data']
            if isinstance(data, list) and len(data) > 0:
                print(f"📋 Found {len(data)} items")
                print(f"📝 First item keys: {list(data[0].keys())}")
            elif isinstance(data, dict):
                print(f"📋 Data structure: {list(data.keys())}")
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
    
    # Print cookie information
    print(f"\n🍪 Cookie Information:")
    cookie_info = client.get_cookies_info()
    print(f"   Total cookies loaded: {cookie_info['total_cookies']}")
    print(f"   Session cookies: {len(cookie_info['session_cookies'])}")


if __name__ == "__main__":
    main() 