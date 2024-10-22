import os
import openai
from datetime import datetime


def create_news_summary_prompt(url: str, dom_content: str):
    system_prompt = """You are a technical news analyzer. Your task is to identify and summarize all distinct news articles from the provided content. Each article should be thoroughly analyzed and summarized independently.

Key Requirements:
1. Articles are written today
2. Identify each separate article in the content
3. Provide detailed summaries that capture the essential information
4. Maintain technical accuracy while ensuring clarity
5. Include quotes and specific technical details when present
6. Preserve dates, version numbers, and specific metrics mentioned"""

    user_prompt = f"""URL: {url}

Analyze all articles writen on {datetime.today()} in the following content. Articles are separated by '---ARTICLE SEPARATOR---'.
Create a detailed summary for each distinct article found:

{dom_content}

Format each article summary using this exact structure:

===ARTICLE START===
METADATA:
- Title: [Extract or derive from content]
- Date: [If mentioned, format as YYYY-MM-DD, otherwise "Not specified"]
- Category: [Technical category/topic]
- URL: [url to article]

ARTICLE SUMMARY:
[5-7 paragraphs detailing the main content, developments, and significance]

TECHNICAL DETAILS:
[List all specific technical information, including:]
- Version numbers
- Specifications
- Technologies mentioned
- Performance metrics
- Compatible systems/platforms
- APIs or protocols discussed

KEY POINTS:
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]
- [Bullet point 4]
- [Bullet point 5]
[Add more if necessary]

COMPANIES/PRODUCTS MENTIONED:
- [List all relevant companies and products]

QUOTES:
[If present, include key quotes from the article]

CONTEXT & IMPLICATIONS:
[1-2 paragraphs about broader impact and context]
===ARTICLE END===

[Repeat structure for each distinct article found]

ANALYSIS SUMMARY:
- Total Articles Found: [number]
- Primary Topics Covered: [list]
- Key Technologies Featured: [list]"""

    return system_prompt, user_prompt

def analyze_webpage(url, dom_content):
    system_prompt, user_prompt = create_news_summary_prompt(url, dom_content)
    
    client = openai.OpenAI(
        api_key=os.environ.get("SAMBANOVA_API_KEY"),
        base_url="https://api.sambanova.ai/v1",
    )
    try:
        response = client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=os.getenv("TEMPERATURE"),
            top_p=os.getenv("TOP_P"),
            max_tokens=os.getenv("TOKEN_AMOUNT")         
        )
    except Exception as e:
        print(f"Error calling API: {e}")
        return None

    return response.choices[0].message.content
