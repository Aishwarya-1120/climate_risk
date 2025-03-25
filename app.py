import os
import json
from dotenv import load_dotenv
import streamlit as st
from serpapi import GoogleSearch
from newsapi import NewsApiClient

load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def search_google_news(query, num_results=5):
    search = GoogleSearch({
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "tbm": "nws",  
        "num": num_results
    })
    results = search.get_dict()
    articles = results.get("news_results", [])
    return [{"title": article.get("title"),
             "source": article.get("source"),
             "date": article.get("date"),
             "snippet": article.get("snippet"),
             "link": article.get("link"),
             "tags": ["climate", "insurance"]} for article in articles]

def search_newsapi(query, num_results=5):
    articles = newsapi.get_everything(q=query, language='en', page_size=num_results)
    return [{"title": article.get("title"),
             "source": article.get("source", {}).get("name"),
             "date": article.get("publishedAt"),
             "snippet": article.get("description"),
             "link": article.get("url"),
             "tags": ["climate", "insurance"]} for article in articles.get("articles", [])]

def load_research_papers():
    with open("data/research_papers.json", "r") as file:
        return json.load(file)

def filter_by_tag(data, selected_tag):
    return [item for item in data if "tags" in item and selected_tag in item["tags"]]

def get_all_tags(datasets):
    tags = set()
    for data in datasets:
        for item in data:
            if "tags" in item:  
                tags.update(item["tags"])
    return sorted(tags)

st.title("🌍 Climate Risk & Insurance Dashboard")
st.sidebar.header("Filters")

user_query = st.sidebar.text_input("🔍 Search News", value="climate risk insurance")
num_results = st.sidebar.slider("📊 Number of Results", 1, 10, 5)

st.sidebar.markdown("### 📡 Search Sources")
use_serpapi = st.sidebar.checkbox("Use Google Search (SerpAPI)", value=True)
use_newsapi = st.sidebar.checkbox("Use NewsAPI", value=True)

news_articles = []

if use_serpapi:
    news_articles.extend(search_google_news(user_query, num_results))

if use_newsapi:
    news_articles.extend(search_newsapi(user_query, num_results))


research_papers = load_research_papers()

all_tags = get_all_tags([news_articles, research_papers])
selected_tag = st.sidebar.selectbox("🗂️ Select a tag", all_tags)

filtered_news = filter_by_tag(news_articles, selected_tag)
filtered_research = filter_by_tag(research_papers, selected_tag)


st.header(f"📰 News Articles Tagged: {selected_tag}")
if filtered_news:
    for article in filtered_news:
        st.subheader(article.get("title"))
        st.caption(f"📌 Source: {article.get('source')} | 🗓️ Published: {article.get('date')}")
        st.write(article.get("snippet", "No summary available."))
        st.markdown(f"[📖 Read more]({article.get('link')})")
        st.markdown("---")
else:
    st.write("🚫 No matching news articles found.")


st.header(f"📚 Research Papers Tagged: {selected_tag}")
if filtered_research:
    for paper in filtered_research:
        st.subheader(paper["title"])
        st.caption(f"👨‍🔬 Authors: {paper['authors']} | 📅 Date: {paper['date']}")
        st.write(paper["abstract"])
        st.markdown("---")
else:
    st.write("🚫 No matching research papers found.")

st.sidebar.info("Explore the latest research and news on climate risk in the insurance industry.")
