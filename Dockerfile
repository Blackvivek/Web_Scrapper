FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    wget \
    firefox-esr \
    --no-install-recommends && \
    # Download latest Geckodriver
    GECKO_VERSION=$(wget -qO- https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep 'tag_name' | cut -d '"' -f 4) && \
    wget -q https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/geckodriver-$GECKO_VERSION-linux64.tar.gz && \
    tar -xzf geckodriver-$GECKO_VERSION-linux64.tar.gz -C /usr/local/bin && \
    rm geckodriver-$GECKO_VERSION-linux64.tar.gz && \
    rm -rf /var/lib/apt/lists/*



RUN  pip install -r requirements.txt

COPY . .

CMD [ "streamlit","run","app.py" ]

