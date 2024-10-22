import os, time
from dotenv import load_dotenv
load_dotenv()

from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection

from bs4 import BeautifulSoup
import re

def scrape_website(website: str):
    try:
        sbr_connection = ChromiumRemoteConnection(os.getenv("CHROME_DRIVER"), 'goog', 'chrome')
        print(f'Connecting to Scraping Browser {website} ...')
        with Remote(sbr_connection, options=ChromeOptions(), keep_alive=True) as driver:
            print('Connected! Navigating...')
            driver.get(website)

            solve_res = driver.execute('executeCdpCommand', {
                'cmd': 'Captcha.waitForSolve',
                'params': {'detectTimeout': 10000}
            })

            print('Captcha solve status:', solve_res['value']['status'])
            print('Navigated! Scraping page content...')
            html = driver.page_source
            # driver.close()
            return html

    except Exception as e:
        print(f"An error occurred: {e}")


def extract_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    print("extracting content...")

    body_content = soup.body

    if body_content:
        return str(body_content)
    return ""

def preprocess_dom_content(dom_content: str) -> str:
    """
    Preprocess the DOM content to extract relevant article text and remove noise.
    """
    try:
        soup = BeautifulSoup(dom_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 
                                    'aside', 'iframe', 'form', 'button']):
            element.decompose()
            
        # Remove advertisement sections
        ad_identifiers = ['ad', 'ads', 'advertisement', 'banner', 'social', 'share', 
                         'comment', 'popup', 'modal', 'cookie', 'newsletter']
        for identifier in ad_identifiers:
            for element in soup.find_all(class_=re.compile(identifier, re.I)):
                element.decompose()
            for element in soup.find_all(id=re.compile(identifier, re.I)):
                element.decompose()
        
        # Find all articles or main content areas
        articles = []
        
        # Look for specific article elements
        article_elements = soup.find_all(['article', 'div[class*="article"]', 
                                        'div[class*="post"]', 'div[class*="content"]'])
        
        for article in article_elements:
            # Extract text content
            text = article.get_text(strip=True)
            # If there's substantial content, add to articles
            if len(text) > 100:  # Minimum length to be considered an article
                articles.append(text)
        
        # If no articles found, try to find content blocks
        if not articles:
            main_content = soup.find('main') or soup.find(class_=re.compile('main|content'))
            if main_content:
                articles.append(main_content.get_text(strip=True))
        
        # Join articles with clear separation
        processed_content = "\n---ARTICLE SEPARATOR---\n".join(articles)
        
        # Clean up text
        processed_content = re.sub(r'\s+', ' ', processed_content)
        processed_content = re.sub(r'[\n\r\t]', ' ', processed_content)
        
        return processed_content
        
    except Exception as e:
        print(f"Error preprocessing DOM content: {e}")
        return dom_content