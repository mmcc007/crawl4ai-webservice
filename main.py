import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
import logging

logging.basicConfig(level=logging.DEBUG)
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
    
    try:
        # Configure with cache disabled
        browser_config = BrowserConfig(verbose=True)
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.DISABLED,  # Disable caching
            word_count_threshold=10,        # Include content blocks with >10 words
            process_iframes=True,           # Process iframe content
            remove_overlay_elements=True    # Remove popups/modals
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            logger.info("Crawler initialized, starting crawl...")
            result = await crawler.arun(
                url=request.url,
                config=run_config
            )
            
            logger.info(f"Crawl completed. Success: {result.success}")
            
            if result.success:
                return {
                    "result": result.markdown,
                    "metadata": {
                        "success": True,
                        "status_code": result.status_code
                    }
                }
            else:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Crawling failed: {result.error_message}"
                )
    except Exception as e:
        logger.error(f"Crawl error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=11235, reload=True)