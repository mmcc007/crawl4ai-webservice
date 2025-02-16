#!/usr/bin/env python3
import argparse
import requests
import sys
import json
import os
from typing import Optional, Dict, Any
from urllib.parse import urlparse

def get_api_token() -> str:
    """Get API token from environment variable."""
    token = os.getenv('CRAWL4AI_API_TOKEN')
    if not token:
        print("Error: CRAWL4AI_API_TOKEN environment variable is not set")
        sys.exit(1)
    return token

def crawl_url(url: str, host: str = "localhost", port: int = 11235) -> Dict[str, Any]:
    """
    Call the crawl service for a given URL.
    
    Args:
        url (str): The URL to crawl
        host (str): The hostname where the service is running
        port (int): The port number of the service
        
    Returns:
        dict: The crawl results
    """
    # Determine if we should use HTTPS (for Render.com and other cloud hosts)
    is_cloud_host = not host.startswith(('localhost', '127.0.0.1'))
    protocol = 'https' if is_cloud_host else 'http'
    
    # For cloud hosts, we don't explicitly specify the port in the URL
    base_url = f"{protocol}://{host}"
    if not is_cloud_host:
        base_url = f"{base_url}:{port}"
    
    endpoint = f"{base_url}/crawl"
    api_token = get_api_token()
    
    # Prepare the request payload
    payload = {
        "urls": url,
        "priority": 10
    }
    
    # Prepare headers with authentication
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # First check if the service is healthy
        # health_check = requests.get(f"{base_url}/health")
        # if health_check.status_code != 200:
        #     print("Error: Crawl service is not healthy")
        #     sys.exit(1)
            
        # Make the crawl request
        response = requests.post(endpoint, json=payload, headers=headers)
        
        # Check if request was successful
        response.raise_for_status()
        
        result = response.json()
        
        # If we got a task ID, automatically check its status
        if 'task_id' in result:
            print(f"Task ID: {result['task_id']}")
            task_status = requests.get(
                f"{base_url}/task/{result['task_id']}", 
                headers=headers
            )
            if task_status.status_code == 200:
                print(f"Task Status: {task_status.json()}")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to crawl service at {endpoint}")
        print("Make sure the service is running and the host/port are correct")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        sys.exit(1)

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Call the crawl service for a URL')
    parser.add_argument('url', help='The URL to crawl')
    parser.add_argument('--host', default='localhost', help='Hostname of the crawl service')
    parser.add_argument('--port', type=int, default=11235, help='Port number of the crawl service')
    
    args = parser.parse_args()
    
    # Call the crawl service
    result = crawl_url(args.url, args.host, args.port)
    
    # Print the results
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()