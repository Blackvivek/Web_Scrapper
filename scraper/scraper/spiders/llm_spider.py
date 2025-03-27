import json
from json.decoder import JSONDecodeError
from logging import getLogger
import os
from urllib.parse import urlparse, urljoin

import requests
import scrapy
from html2text import HTML2Text

html_cleaner = HTML2Text()
logger = getLogger(__name__)


class LLMSpider(scrapy.Spider):
    name = "llm_spider"

    def __init__(self, url=None, depth=2, output_dir="scraped_data", *args, **kwargs):
        super(LLMSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.allowed_domains = [urlparse(url).netloc]
        self.max_depth = int(depth)
        self.output_dir = os.path.join(output_dir, urlparse(url).netloc)
        self.visited_urls = set()
        os.makedirs(self.output_dir, exist_ok=True)

    def parse(self, response, **kwargs):
        current_depth = kwargs.get("depth", 1)
        if current_depth > self.max_depth:
            return

        self.visited_urls.add(response.url)

        # Extract raw text and clean it
        raw_html = response.text
        cleaned_text = html_cleaner.handle(raw_html)
        
        # Extract code snippets
        raw_code = "\n".join(response.css("pre code::text, code::text, pre::text").getall())
        
        # Process with LLM
        structured_data = self.process_with_llm(cleaned_text, raw_code)

        # Save structured data
        self.save_data(structured_data, response.url)

        # Crawl sublinks
        for href in response.css("a::attr(href)").getall():
            absolute_url = urljoin(response.url, href)
            if urlparse(absolute_url).netloc in self.allowed_domains and absolute_url not in self.visited_urls:
                yield response.follow(absolute_url, callback=self.parse, cb_kwargs={"depth": current_depth + 1})

    def process_with_llm(self, cleaned_text, raw_code):
        """ Send parsed text and code to Llama 2 """
        url = "http://127.0.0.1:11434/api/generate"

        prompt = f"""Format the following data into a structured JSON with clear separation of text and code sections.
        
        ### TEXT:
        {cleaned_text}

        ### CODE:
        {raw_code}
        """

        payload = {
            "model": "llama2",
            "messages": [
                {"role": "system", "content": "You are an AI that formats scraped web data into structured JSON."},
                {"role": "user", "content": prompt}
            ]
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)

        try:
            response_json = response.json()
            if "response" in response_json:
                json_content = response_json["response"].strip()
                return json.loads(json_content)
            else:
                return {"text": cleaned_text, "code": raw_code}  # Fallback if LLM fails
        except (JSONDecodeError, KeyError) as e:
            logger.error(f"Error processing LLM response: {e}")
            return {"text": cleaned_text, "code": raw_code}

    def save_data(self, structured_data, page_url):
        """ Save structured data """
        page_name = urlparse(page_url).path.replace("/", "_").strip("_") or "home"
        json_path = os.path.join(self.output_dir, f"{page_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, indent=4)