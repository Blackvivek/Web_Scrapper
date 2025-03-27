# import scrapy
# import os
# import json
# import csv
# from urllib.parse import urlparse, urljoin

# class GenericSpider(scrapy.Spider):
#     name = "generic_spider"

#     def __init__(self, url=None, depth=2, storage_mode="centralized", output_dir="scraped_data", *args, **kwargs):
#         super(GenericSpider, self).__init__(*args, **kwargs)
#         self.start_urls = [url]
#         self.allowed_domains = [urlparse(url).netloc]
#         self.max_depth = int(depth)
#         self.storage_mode = storage_mode
#         self.output_dir = os.path.join(output_dir, urlparse(url).netloc)  # Folder per website
#         self.visited_urls = set()  # Track visited URLs
#         os.makedirs(self.output_dir, exist_ok=True)

#         # CSV File Setup (Only for Centralized Mode)
#         if self.storage_mode == "centralized":
#             self.csv_file = os.path.join(self.output_dir, "scraped_data.csv")
#             if not os.path.exists(self.csv_file):
#                 with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
#                     writer = csv.writer(f)
#                     writer.writerow(["URL", "Content Type", "Content"])  # Header row

#     def parse(self, response, **kwargs):
#         current_depth = kwargs.get('depth', 1)
#         if current_depth > self.max_depth:
#             return  # Stop if depth limit is reached

#         self.visited_urls.add(response.url)  # Mark as visited

#         # Extracting content while preserving order
#         content = []
#         for element in response.css("p, h1, h2, h3, h4, h5, h6, pre code, code, pre, .code, .highlight, .prettyprint, .sourceCode, span.gp, span.n, span.o, span.s2"):
#             if element.root.tag in ["p", "h1", "h2", "h3", "h4", "h5", "h6"]:
#                 content.append({"type": "text", "content": element.get()})
#             else:
#                 content.append({"type": "code", "content": element.get()})

#         page_data = {
#             "url": response.url,
#             "content": content  # Stores as a structured list
#         }

#         # Save data in JSON and CSV
#         self.save_data(page_data)

#         # Extract and follow sublinks
#         for href in response.css("a::attr(href)").getall():
#             absolute_url = urljoin(response.url, href)
#             parsed_url = urlparse(absolute_url)

#             # Check if URL is valid and belongs to the same domain
#             if parsed_url.netloc in self.allowed_domains and absolute_url not in self.visited_urls:
#                 yield response.follow(absolute_url, callback=self.parse, cb_kwargs={"depth": current_depth + 1})

#     def save_data(self, page_data):
#         """ Save scraped data in JSON and CSV formats """

#         if self.storage_mode == "centralized":
#             # Save to JSON (Append to existing JSON file)
#             json_path = os.path.join(self.output_dir, "scraped_data.json")
#             existing_data = []
#             if os.path.exists(json_path):
#                 with open(json_path, "r", encoding="utf-8") as f:
#                     existing_data = json.load(f)

#             existing_data.append(page_data)
#             with open(json_path, "w", encoding="utf-8") as f:
#                 json.dump(existing_data, f, indent=4)

#             # Save to CSV
#             with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
#                 writer = csv.writer(f)
#                 for item in page_data["content"]:
#                     writer.writerow([page_data["url"], item["type"], item["content"]])

#         else:
#             # Save as separate JSON and CSV files per page
#             page_name = urlparse(page_data["url"]).path.replace("/", "_").strip("_") or "home"
#             json_path = os.path.join(self.output_dir, f"{page_name}.json")
#             csv_path = os.path.join(self.output_dir, f"{page_name}.csv")

#             with open(json_path, "w", encoding="utf-8") as f:
#                 json.dump(page_data, f, indent=4)

#             with open(csv_path, "w", newline="", encoding="utf-8") as f:
#                 writer = csv.writer(f)
#                 writer.writerow(["Content Type", "Content"])
#                 for item in page_data["content"]:
#                     writer.writerow([item["type"], item["content"]])
import scrapy
import os
import json
import csv
import time
from urllib.parse import urlparse, urljoin
from html2text import HTML2Text
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

class GenericSpider(scrapy.Spider):
    name = "generic_spider"

    def __init__(self, url=None, depth=2, storage_mode="centralized", output_dir="scraped_data", use_selenium=True, *args, **kwargs):
        super(GenericSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.allowed_domains = [urlparse(url).netloc]
        self.max_depth = int(depth)
        self.storage_mode = storage_mode
        self.output_dir = os.path.join(output_dir, urlparse(url).netloc)
        self.visited_urls = set()
        os.makedirs(self.output_dir, exist_ok=True)

        self.use_selenium = use_selenium  # Enable Selenium for JavaScript-rendered pages

        # HTML Cleaner
        self.html_cleaner = HTML2Text()
        self.html_cleaner.ignore_links = True
        self.html_cleaner.ignore_images = True
        self.html_cleaner.ignore_emphasis = True

        # CSV File Setup (Centralized Mode)
        if self.storage_mode == "centralized":
            self.csv_file = os.path.join(self.output_dir, "scraped_data.csv")
            if not os.path.exists(self.csv_file):
                with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["URL", "Title", "Cleaned Text", "Code Snippets"])  

        # Selenium WebDriver Setup (Headless Firefox)
        if self.use_selenium:
            options = Options()
            options.add_argument("--headless")  
            self.driver = webdriver.Firefox(options=options)

    def parse(self, response, **kwargs):
        current_depth = kwargs.get('depth', 1)
        if current_depth > self.max_depth:
            return  

        self.visited_urls.add(response.url)  

        # Extract text using Selenium if enabled
        if self.use_selenium:
            cleaned_text, code_snippets = self.extract_with_selenium(response.url)
        else:
            cleaned_text, code_snippets = self.extract_with_scrapy(response)

        page_data = {
            "url": response.url,
            "title": response.css("title::text").get(),
            "cleaned_text": cleaned_text,
            "code_snippets": code_snippets,
        }

        self.save_data(page_data)

        # Extract and follow sublinks
        for href in response.css("a::attr(href)").getall():
            absolute_url = urljoin(response.url, href)
            parsed_url = urlparse(absolute_url)

            if parsed_url.netloc in self.allowed_domains and absolute_url not in self.visited_urls:
                yield response.follow(absolute_url, callback=self.parse, cb_kwargs={"depth": current_depth + 1})

    def extract_with_scrapy(self, response):
        """ Extracts text and code snippets using Scrapy (for static pages) """
        raw_html = "\n".join(response.css("p, h1, h2, h3, li").getall())
        cleaned_text = self.html_cleaner.handle(raw_html).strip()
        code_snippets = "\n".join(response.css("pre code, code, pre").getall()).strip()
        return cleaned_text, code_snippets

    def extract_with_selenium(self, url):
        """ Uses Selenium to render JavaScript-heavy pages and extract content """
        self.driver.get(url)
        time.sleep(3)  # Wait for JavaScript to load (Adjust based on website speed)

        # Extract page source
        page_source = self.driver.page_source

        # Process with HTML2Text
        cleaned_text = self.html_cleaner.handle(page_source).strip()

        # Extract code snippets
        # code_elements = self.driver.find_elements(By.CSS_SELECTOR, "pre code, code, pre")
        # code_snippets = "\n".join([element.text for element in code_elements]).strip()

        return cleaned_text, code_snippets

    def save_data(self, page_data):
        """ Save scraped data in JSON and CSV formats """

        if self.storage_mode == "centralized":
            json_path = os.path.join(self.output_dir, "scraped_data.json")
            existing_data = []
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

            existing_data.append(page_data)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4)

            with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([page_data["url"], page_data["title"], page_data["cleaned_text"], page_data["code_snippets"]])
        else:
            page_name = urlparse(page_data["url"]).path.replace("/", "_").strip("_") or "home"
            json_path = os.path.join(self.output_dir, f"{page_name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(page_data, f, indent=4)

            csv_path = os.path.join(self.output_dir, f"{page_name}.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["URL", "Title", "Cleaned Text", "Code Snippets"])
                writer.writerow([page_data["url"], page_data["title"], page_data["cleaned_text"], page_data["code_snippets"]])

    def closed(self, reason):
        """ Close the Selenium WebDriver when Scrapy finishes """
        if self.use_selenium:
            self.driver.quit()
