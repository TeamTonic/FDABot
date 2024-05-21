# src/webscrapper.py
# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import aiofiles
import xml.etree.ElementTree as ET
import json
import nest_asyncio
import os


nest_asyncio.apply()

class WebScrapper:
    def __init__(self, max_concurrency=5, api_key=None):
        self.max_concurrency = max_concurrency
        self.api_key = api_key
        self.progress_lock = asyncio.Lock()

    async def fetch(self, session, url, headers, semaphore):
        async with semaphore:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Ensure we raise an error for bad responses
                if 'application/json' in response.headers.get('Content-Type'):
                    return await response.json()
                else:
                    raise aiohttp.ContentTypeError(
                        request_info=response.request_info,
                        history=response.history,
                        message=f"Unexpected content type: {response.headers.get('Content-Type')}"
                    )

    async def fetch_content(self, session, url, semaphore, progress, total):
        headers_common = {
            "Accept": "application/json",
        }

        if self.api_key:
            headers_common["Authorization"] = f"Bearer {self.api_key}"

        headers_html = headers_common.copy()
        headers_html["X-Return-Format"] = "html"

        headers_markdown = headers_common.copy()
        headers_markdown["X-Return-Format"] = "markdown"

        try:
            url1 = f"https://r.jina.ai/{url}"

            # full html before the filtering pipeline, consume MOST tokens!
            response_html = self.fetch(session, url1, headers_html, semaphore)

            # html->markdown but without smart filtering
            response_markdown = self.fetch(session, url1, headers_markdown, semaphore)

            # default content behavior as if u access via https://r.jina.ai/url
            response_default = self.fetch(session, url1, headers_common, semaphore)

            html, markdown, default = await asyncio.gather(response_html, response_markdown, response_default)

            result = {
                'url': url,
                'default': default.get('data').get('content'),
                'html': html.get('data').get('html'),
                'markdown': markdown.get('data').get('content'),
            }
                # Save markdown content to a file
            if result['markdown']:
                filename = os.path.join('markdown', f"{self.url_to_filename(url)}.md")
                async with aiofiles.open(filename, 'w') as f:
                    await f.write(result['markdown'])
        
        except aiohttp.ContentTypeError as e:
            print(f"Skipping URL due to content type error: {url}")
            result = {
                'url': url,
                'default': None,
                'html': None,
                'markdown': None,
            }

        async with self.progress_lock:
            progress['completed'] += 1
            print(f"Completed {progress['completed']} out of {total} requests")

        return result

    def url_to_filename(self, url):
        return url.strip().replace('https://', '').replace('http://', '').replace('/', '_')


    async def fetch_sitemap_urls(self, sitemap_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(sitemap_url) as response:
                response.raise_for_status()
                sitemap_xml = await response.text()

        root = ET.fromstring(sitemap_xml)
        urls = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        return urls

    async def fetch_all_content(self, sitemap_url):
        urls = await self.fetch_sitemap_urls(sitemap_url)
        total_urls = len(urls)
        progress = {'completed': 0}
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_content(session, url, semaphore, progress, total_urls) for url in urls]
            results = await asyncio.gather(*tasks)

        async with aiofiles.open('website.json', 'w') as f:
            await f.write(json.dumps(results, indent=4))

    def run(self, sitemap_url):
        # Ensure the markdown directory exists
        os.makedirs('markdown', exist_ok=True)
        asyncio.run(self.fetch_all_content(sitemap_url))

# # Example usage
# if __name__ == "__main__":
#     sitemap_url = "https://jina.ai/sitemap.xml"
    
#     # Without API Key
#     scrapper = WebScrapper(max_concurrency=3)
#     scrapper.run(sitemap_url)
    
#     # With API Key
#     api_key = 'jina_fd455547319d4057809186abfa89d22975L7a1mgzYgAXTcuHkfyYC433GTP'
#     scrapper_with_key = WebScrapper(max_concurrency=10, api_key=api_key)
#     scrapper_with_key.run(sitemap_url)