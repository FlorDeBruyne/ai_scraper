# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.10-x86_64

# Install necessary packages
RUN yum install -y \
    unzip \
    xorg-x11-server-Xvfb \
    dbus-glib \
    libXtst \
    libXrandr \
    libXcursor \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    libXdamage \
    libXext \
    libXi \
    libXScrnSaver \
    pango \
    at-spi2-atk \
    libXt \
    nss \
    mesa-libgbm

# Install Chrome
RUN curl -SL https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm -o google-chrome.rpm && \
    yum -y install ./google-chrome.rpm && \
    rm google-chrome.rpm

# Install ChromeDriver
RUN curl -SL https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip -o chromedriver.zip && \
    unzip chromedriver.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm chromedriver.zip

# Copy function code and requirements
COPY src/scrape.py ./
COPY requirements.txt ./requirements.txt
COPY src/parser.py ./
COPY .env ./.env

# Install dependencies
RUN pip install --no-cache-dir -r ./requirements.txt

# Set the CMD to your handler
CMD ["scrape.lambda_handler"]