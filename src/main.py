import streamlit as st
from tqdm import tqdm
from scrape import scrape_website, preprocess_dom_content, extract_content
from parser import analyze_webpage, save_summary

results = []

st.title("AI Web Scraper")
website = st.text_input("Enter the URLs of the websites you want to scrape (comma separated):")

if st.button("Scrape the site"):
    print(f"Scraping {website}")
    result = scrape_website(website)
    body_content = extract_content(result)
    cleaned_content = preprocess_dom_content(body_content)

    st.session_state.dom_content = cleaned_content

    with st.expander("View DOM Content:"):
        st.text_area("DOM Content", cleaned_content, height=250)

if "dom_content" in st.session_state:
    # dom_chunks = split_dom_content(st.session_state.dom_content)
    parsed_result = analyze_webpage(website, st.session_state.dom_content)
    save_summary(parsed_result, website)

    st.write(parsed_result)


    




