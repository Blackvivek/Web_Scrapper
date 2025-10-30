import streamlit as st
import subprocess
import json
import os
import pandas as pd
from urllib.parse import urlparse

st.title("🔍 Web Scraper")

# User input for URL
url = st.text_input("🌐 Enter the URL to scrape:")

# Depth selection
depth = st.slider("📌 Select Depth of Crawling:", 1, 5, 2)

# Storage option selection
storage_option = st.radio(
    "📂 Choose Storage Mode:",
    ("Centralized (Single JSON File)", "Decentralized (Separate JSON Files)")
)

# Convert selection to format for Scrapy
storage_mode = "centralized" if "Centralized" in storage_option else "decentralized"

# **Scraper Selection**: User can choose between Generic Scraper and LLM Scraper
scraper_type = st.radio("🛠 Choose Scraper Type:", ["Generic Scraper", "LLM Scraper"])

# Function to create a unique folder based on the website name
def get_unique_folder_name(base_folder, website_name):
    folder_path = os.path.join(base_folder, website_name)
    count = 1
    while os.path.exists(folder_path):
        folder_path = os.path.join(base_folder, f"{website_name}_{count}")
        count += 1
    return folder_path

# Button to start scraping
if st.button("🚀 Start Scraping"):
    if url:
        # Extract domain name from the URL
        parsed_url = urlparse(url)
        website_name = parsed_url.netloc.replace(".", "_")

        # Create a unique folder for each scrape session
        base_scrape_dir = "scraped_data"
        scrape_dir = get_unique_folder_name(base_scrape_dir, website_name)
        os.makedirs(scrape_dir, exist_ok=True)

        # Choose the scraper script based on user selection
        scraper_script = "scraper/scraper/spiders/genericspider.py" if scraper_type == "Generic Scraper" else "scraper/scraper/spiders/llm_spider.py"

        # Run Scrapy as a subprocess with selected scraper
        cmd = [
            "scrapy", "runspider", f"{scraper_script}",
            "-a", f"url={url}", "-a", f"depth={depth}",
            "-a", f"storage_mode={storage_mode}",
            "-a", f"output_dir={scrape_dir}"
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logs, errors = process.communicate()

        # Display Scrapy logs
        st.text_area("📜 Scrapy Logs", logs, height=200)
        if errors:
            st.text_area("❌ Errors", errors, height=100)

        # Display scraped data if centralized storage mode is selected
        centralized_file = os.path.join(scrape_dir, "scraped_data.json")
        if storage_mode == "centralized" and os.path.exists(centralized_file):
            with open(centralized_file, "r", encoding="utf-8") as f:
                scraped_data = json.load(f)

            st.write(f"### 📜 Scraped Data (Stored in `{scrape_dir}`)")
            st.json(scraped_data)

            # Extract and display links
            all_links = []
            for page in scraped_data:
                for link in page.get("links", []):
                    all_links.append({"Page": page["url"], "Link": link})

            if all_links:
                st.write("### 🔗 Extracted Links")
                df = pd.DataFrame(all_links)
                st.dataframe(df)

            # Extract and display images
            all_images = []
            for page in scraped_data:
                for img in page.get("images", []):
                    all_images.append({"Page": page["url"], "Image": img})

            if all_images:
                st.write("### 🖼 Extracted Images")
                for img_data in all_images:
                    st.image(img_data["Image"], caption=img_data["Page"])

            # Provide download links
            st.write("### 📥 Download Scraped Data")
            st.download_button("📂 Download JSON", json.dumps(scraped_data, indent=4), file_name="scraped_data.json", mime="application/json")
            if os.path.exists(os.path.join(scrape_dir, "scraped_data.csv")):
                st.download_button("📂 Download CSV", open(os.path.join(scrape_dir, "scraped_data.csv"), "rb"), file_name="scraped_data.csv")

    else:
        st.warning("❌ Please enter a valid URL!")
