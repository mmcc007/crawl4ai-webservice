import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

app = FastAPI(title="Crawl4AI Web Service")

# Request body for a crawl job.
class CrawlRequest(BaseModel):
    url: str
    priority: int = 10  # Optional parameter; adjust as needed

# Health-check endpoint.
@app.get("/health")
async def health():
    return {"status": "ok"}

# Synchronous crawl endpoint.
@app.post("/crawl")
async def crawl_endpoint(request: CrawlRequest):
    # Set up browser and crawl configurations.
    browser_config = BrowserConfig(headless=True)
    crawl_config = CrawlerRunConfig()
    
    # Create and run the asynchronous crawler.
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=request.url, config=crawl_config)
        
    if result.success:
        return {"result": result.markdown}
    else:
        raise HTTPException(status_code=500, detail="Crawling failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=11235, reload=True)

