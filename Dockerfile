# Use Python 3.12
FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    imagemagick \
    procps \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Geckodriver
RUN GECKO_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep tag_name | cut -d '"' -f 4) \
    && wget -q https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/geckodriver-$GECKO_VERSION-linux64.tar.gz \
    && tar -xzf geckodriver-$GECKO_VERSION-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-$GECKO_VERSION-linux64.tar.gz

# Set ImageMagick policy to allow reading/writing
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/g' /etc/ImageMagick-6/policy.xml

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn python-multipart

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application
# We will use uvicorn to run our FastAPI app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
