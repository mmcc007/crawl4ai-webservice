#!/usr/bin/env python3
import argparse
import requests
import sys
import json

def crawl_url(url, host="localhost", port=11235):
    """
    Call the crawl service for a given URL.
    
    Args:
        url (str): The URL to crawl
        host (str): The hostname where the service is running
        port (int): The port number of the service
        
    Returns:
        dict: The crawl results
    """
    endpoint = f"http://{host}:{port}/crawl"
    
    # Prepare the request payload
    payload = {
        "url": url,
        "priority": 10
    }
    
    try:
        # First check if the service is healthy
        health_check = requests.get(f"http://{host}:{port}/health")
        if health_check.status_code != 200:
            print("Error: Crawl service is not healthy")
            sys.exit(1)
            
        # Make the crawl request
        response = requests.post(endpoint, json=payload)
        
        # Check if request was successful
        response.raise_for_status()
        
        return response.json()
        
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
