#!/bin/bash

# Environment variables
API_URL="https://crawl4ai-nulk.onrender.com"  # Change this to your API URL
API_TOKEN="6f71f811-8570-48b7-877a-f443565844ed"       # Replace with your API token

# Basic crawl with single URL
curl -X POST "${API_URL}/crawl" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": "https://example.com",
    "word_count_threshold": 1,
    "screenshot": false,
    "magic": false,
    "priority": 5
  }'

# Advanced crawl with multiple URLs and extraction config
curl -X POST "${API_URL}/crawl" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/page1",
      "https://example.com/page2"
    ],
    "extraction_config": {
      "type": "basic",
      "params": {}
    },
    "chunking_strategy": {
      "type": "paragraph",
      "params": {}
    },
    "content_filter": {
      "type": "bm25",
      "params": {}
    },
    "cache_mode": "enabled",
    "ttl": 3600
  }'

# Crawl with JavaScript execution
curl -X POST "${API_URL}/crawl" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": "https://example.com",
    "js_code": [
      "window.scrollTo(0, document.body.scrollHeight)",
      "await new Promise(r => setTimeout(r, 2000))"
    ],
    "wait_for": ".content-loaded",
    "css_selector": "main"
  }'

# Crawl with LLM extraction
curl -X POST "${API_URL}/crawl" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": "https://example.com",
    "extraction_config": {
      "type": "llm",
      "params": {
        "model": "default",
        "prompt": "Extract main content"
      }
    },
    "magic": true
  }'

# Crawl with screenshot and custom session
curl -X POST "${API_URL}/crawl" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": "https://example.com",
    "screenshot": true,
    "session_id": "custom-session-1",
    "crawler_params": {
      "viewport": {"width": 1920, "height": 1080},
      "timeout": 30000
    }
  }'

# Function to check task status
check_task_status() {
    local task_id=$1
    curl -X GET "${API_URL}/task/${task_id}" \
      -H "Authorization: Bearer ${API_TOKEN}" \
      -H "Content-Type: application/json"
}

# Example usage:
# check_task_status "your-task-id-here"
