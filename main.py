import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Crawl4AI Web Service")

class CrawlRequest(BaseModel):
    url: str
    priority: int = 10

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/crawl")
async def crawl_endpoint(request: CrawlRequest):
    logger.info(f"Starting crawl for URL: {request.url}")
    
    browser_config = BrowserConfig(headless=True)
    crawl_config = CrawlerRunConfig()
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            logger.info("Crawler initialized, starting crawl...")
            result = await crawler.arun(url=request.url, config=crawl_config)
            logger.info(f"Crawl completed. Success: {result.success}")
            logger.info(f"Result content length: {len(result.markdown) if result.markdown else 0}")
            
            if result.success:
                return {"result": result.markdown, "metadata": {"success": True}}
            else:
                raise HTTPException(status_code=500, detail="Crawling failed")
    except Exception as e:
        logger.error(f"Crawl error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=11235, reload=True)