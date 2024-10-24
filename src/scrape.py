import os, time, json, re


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

def lambda_handler(event, context):
    # Extract the URL from the event
    website = event.get('website')
    if not website:
        return {
            'statusCode': 400,
            'body': 'No website URL provided in the event.'
        }
    # Call the scrape_website function
    html_content = scrape_website(website)
    if html_content is None:
        return {
            'statusCode': 500,
            'body': 'Failed to scrape the website.'
        }

    # Process the HTML content
    extracted_content = extract_content(html_content)
    processed_content = preprocess_dom_content(extracted_content)

    return {
        'statusCode': 200,
        'body': processed_content
    }

def scrape_website(website: str):
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')

    print(f'Connecting to Scraping Browser {website} ...')
    try:
        with webdriver.Chrome(options=options) as driver:
            print('Connected! Navigating...')
            driver.get(website)

            # Handle Captcha if necessary
            solve_res = driver.execute('executeCdpCommand', {
                'cmd': 'Captcha.waitForSolve',
                'params': {'detectTimeout': 10000}
            })

            print('Captcha solve status:', solve_res['value']['status'])
            print('Navigated! Scraping page content...')

            html = driver.page_source
            return html

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        driver.quit()


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