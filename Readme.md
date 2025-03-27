# Web Scrapper

## Description
This project is a web scraper built using **Scrapy** for backend scraping and **Streamlit** for the frontend interface. It is designed to extract data from websites efficiently and supports multiple formats for data export. The project is highly customizable.

---

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd Web\ Scrapper
   ```

3. Create and activate a Python virtual environment:
   ```bash
   python -m venv web_env
   web_env\Scripts\activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
1. **Run the Scrapy Spider**:
   To start the web scraper, use the following command:
   ```bash
   scrapy crawl <spider-name>
   ```

2. **Run the Streamlit Frontend**:
   To launch the Streamlit interface, use:
   ```bash
   streamlit run app.py
   ```

3. **Configure the Scraper**:
   - Update the target URL and scraping options in the `config.json` file or directly in the spider files.
   - View the scraped data in the `output` folder.

---

## Contribution
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License
This project is licensed under the MIT License.