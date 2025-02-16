#!/usr/bin/env python3
import argparse
import requests
import sys
import json
import os
import time
from typing import Optional, Dict, Any, Literal
from urllib.parse import urlparse

CrawlMode = Literal['async', 'sync', 'direct']

def get_api_token() -> str:
    """Get API token from environment variable."""
    token = os.getenv('CRAWL4AI_API_TOKEN')
    if not token:
        print("Error: CRAWL4AI_API_TOKEN environment variable is not set")
        sys.exit(1)
    return token

def wait_for_task_completion(base_url: str, task_id: str, headers: Dict[str, str], max_wait: int = 60) -> Dict[str, Any]:
    """Poll task status until completion or timeout."""
    start_time = time.time()
    polling_interval = 2
    
    while True:
        if time.time() - start_time > max_wait:
            print(f"Timeout waiting for task completion after {max_wait} seconds")
            sys.exit(1)
            
        response = requests.get(f"{base_url}/task/{task_id}", headers=headers)
        if response.status_code == 200:
            status_data = response.json()
            print(f"Task Status: {status_data.get('status', 'unknown')}")
            
            if status_data.get('status') == 'completed':
                return status_data
            elif status_data.get('status') == 'failed':
                print("Task failed:", status_data.get('error', 'Unknown error'))
                sys.exit(1)
                
        time.sleep(polling_interval)

def save_markdown_result(result: Dict[str, Any], filename: str = 'crawl_result.md') -> None:
    """Save crawl result to markdown file."""
    try:
        # Handle various result formats
        if isinstance(result, dict):
            if 'result' in result:
                markdown_content = result['result']
                if isinstance(markdown_content, dict):
                    if 'markdown' in markdown_content:
                        markdown_content = markdown_content['markdown']
                    else:
                        markdown_content = json.dumps(markdown_content, indent=2)
            else:
                markdown_content = json.dumps(result, indent=2)
        else:
            markdown_content = str(result)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"\nMarkdown result saved to {filename}")
    except Exception as e:
        print(f"Error saving markdown result: {e}")
        sys.exit(1)

def crawl_url(url: str, mode: CrawlMode = 'sync', host: str = "localhost", 
              port: int = 11235) -> Dict[str, Any]:
    """
    Call the crawl service using specified mode.
    
    Args:
        url: The URL to crawl
        mode: 'async', 'sync', or 'direct'
        host: The hostname where the service is running
        port: The port number of the service
    """
    is_cloud_host = not host.startswith(('localhost', '127.0.0.1'))
    protocol = 'https' if is_cloud_host else 'http'
    
    base_url = f"{protocol}://{host}"
    if not is_cloud_host:
        base_url = f"{base_url}:{port}"
    
    # Select endpoint based on mode
    endpoints = {
        'async': '/crawl',
        'sync': '/crawl_sync',
        'direct': '/crawl_direct'
    }
    endpoint = f"{base_url}{endpoints[mode]}"
    
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
        print(f"\nUsing {mode} mode at endpoint: {endpoint}")
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if mode == 'async' and 'task_id' in result:
            task_id = result['task_id']
            print(f"Task ID: {task_id}")
            final_result = wait_for_task_completion(base_url, task_id, headers)
            save_markdown_result(final_result)
            return final_result
        else:
            # Direct or sync mode - result is immediate
            save_markdown_result(result)
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
    parser.add_argument('--mode', choices=['async', 'sync', 'direct'], 
                        default='sync', help='Crawl mode to use')
    
    args = parser.parse_args()
    
    result = crawl_url(args.url, args.mode, args.host, args.port)
    # print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()