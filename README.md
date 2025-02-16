# Crawl4AI Web Service

A web service wrapper around the Crawl4AI library for efficient web content extraction. This service provides both synchronous and asynchronous APIs for crawling web pages and extracting their content in markdown format.

## Features

- Multiple crawling modes:
  - Asynchronous crawling with task tracking
  - Synchronous crawling with direct response
  - Direct mode for minimal overhead
- Bearer token authentication
- Markdown output format
- Support for JavaScript-heavy pages
- Configurable content extraction
- Docker deployment ready

## Prerequisites

- Python 3.10 or higher
- Docker (optional, for containerized deployment)
- Crawl4AI API token

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd crawl4ai-webservice
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
```bash
export CRAWL4AI_API_TOKEN=your_token_here
```

## Usage

### Starting the Service

Run the FastAPI service:
```bash
python main.py
```

The service will start on port 11235 by default.

### Using the Client

The `crawl_client.py` script provides a command-line interface to interact with the service. It supports multiple crawling modes:

```bash
# Synchronous crawling (default)
python crawl_client.py https://example.com

# Asynchronous crawling
python crawl_client.py https://example.com --mode async

# Direct crawling
python crawl_client.py https://example.com --mode direct

# Using a remote host
python crawl_client.py https://example.com --host crawl4ai-nulk.onrender.com
```

### API Endpoints

#### 1. Synchronous Crawling
```bash
POST /crawl_sync
```
- Blocks until crawling is complete
- Returns results directly
- Best for quick crawls

#### 2. Asynchronous Crawling
```bash
POST /crawl
```
- Returns a task ID immediately
- Requires polling `/task/{task_id}` for results
- Ideal for long-running crawls

#### 3. Direct Crawling
```bash
POST /crawl_direct
```
- Minimal processing overhead
- Returns results immediately
- Best for simple crawls

### Example CURL Usage

Basic crawl with authentication:
```bash
curl -X POST "https://your-host/crawl_sync" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": "https://example.com",
    "priority": 10
  }'
```

## Configuration

### Service Configuration

The service can be configured through environment variables:

- `CRAWL4AI_API_TOKEN`: Required for authentication
- `PORT`: Service port (default: 11235)
- `HOST`: Service host (default: 0.0.0.0)

### Crawler Configuration

The crawler can be configured through the API request payload:

```json
{
  "urls": "https://example.com",
  "priority": 10,
  "extraction_config": {
    "type": "basic",
    "params": {}
  },
  "chunking_strategy": {
    "type": "paragraph",
    "params": {}
  }
}
```

## Docker Deployment

1. Build the image:
```bash
docker build -t crawl4ai-webservice .
```

2. Run the container:
```bash
docker run -p 11235:11235 \
  -e CRAWL4AI_API_TOKEN=your_token_here \
  crawl4ai-webservice
```

## Render.com Deployment

The service is configured for deployment on Render.com with the following features:
- Port mappings (8000, 11235, 9222, 8080)
- HTTPS support
- Authentication via Bearer token

## Error Handling

The service provides detailed error messages for common issues:
- Authentication failures
- Connection errors
- Crawling failures
- Invalid URLs

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

[Your License Here]

## Acknowledgments

- Crawl4AI library
- FastAPI framework
- Playwright for web automation
