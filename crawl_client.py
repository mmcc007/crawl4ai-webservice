#!/usr/bin/env python3
import argparse
import requests
import sys
import json
import os
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse

def get_api_token() -> str:
    """Get API token from environment variable."""
    token = os.getenv('CRAWL4AI_API_TOKEN')
    if not token:
        print("Error: CRAWL4AI_API_TOKEN environment variable is not set")
        sys.exit(1)
    return token

def wait_for_task_completion(base_url: str, task_id: str, headers: Dict[str, str], max_wait: int = 60) -> Dict[str, Any]:
    """
    Poll task status until completion or timeout.
    
    Args:
        base_url: Base URL of the service
        task_id: Task ID to check
        headers: Request headers
        max_wait: Maximum wait time in seconds
        
    Returns:
        dict: Final task status and result
    """
    start_time = time.time()
    polling_interval = 2  # seconds
    
    while True:
        if time.time() - start_time > max_wait:
            print(f"Timeout waiting for task completion after {max_wait} seconds")
            sys.exit(1)
            
        response = requests.get(f"{base_url}/task/{task_id}", headers=headers)
        if response.status_code == 200:
            status_data = response.json()
            print(f"Task Status: {status_data.get('status', 'unknown')}")
            
            # Check if task is complete
            if status_data.get('status') == 'completed':
                return status_data
            elif status_data.get('status') == 'failed':
                print("Task failed:", status_data.get('error', 'Unknown error'))
                sys.exit(1)
                
        time.sleep(polling_interval)

def crawl_url(url: str, host: str = "localhost", port: int = 11235, wait_for_result: bool = True) -> Dict[str, Any]:
    """
    Call the crawl service for a given URL and optionally wait for results.
    
    Args:
        url (str): The URL to crawl
        host (str): The hostname where the service is running
        port (int): The port number of the service
        wait_for_result (bool): Whether to wait for task completion
        
    Returns:
        dict: The crawl results
    """
    is_cloud_host = not host.startswith(('localhost', '127.0.0.1'))
    protocol = 'https' if is_cloud_host else 'http'
    
    base_url = f"{protocol}://{host}"
    if not is_cloud_host:
        base_url = f"{base_url}:{port}"
    
    endpoint = f"{base_url}/crawl"
    api_token = get_api_token()
    
    payload = {
        "urls": url,
        "priority": 10
    }
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if 'task_id' in result:
            task_id = result['task_id']
            print(f"\nTask ID: {task_id}")
            
            if wait_for_result:
                final_result = wait_for_task_completion(base_url, task_id, headers)
                if 'result' in final_result:
                    # Handle nested result structure
                    markdown_content = final_result['result'].get('result', '')
                    if isinstance(markdown_content, dict):
                        markdown_content = json.dumps(markdown_content, indent=2)
                    
                    # Save markdown to file
                    with open('crawl_result.md', 'w') as f:
                        f.write(markdown_content)
                    print(f"\nMarkdown result saved to crawl_result.md")
                return final_result
            
        return result
        
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to crawl service at {endpoint}")
        print("Make sure the service is running and the host/port are correct")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Call the crawl service for a URL')
    parser.add_argument('url', help='The URL to crawl')
    parser.add_argument('--host', default='localhost', help='Hostname of the crawl service')
    parser.add_argument('--port', type=int, default=11235, help='Port number of the crawl service')
    parser.add_argument('--no-wait', action='store_true', help='Don\'t wait for task completion')
    
    args = parser.parse_args()
    
    result = crawl_url(args.url, args.host, args.port, wait_for_result=not args.no_wait)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()