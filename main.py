import json
import os
import streamlit as st
import time
from scraper import scrape_tweets  # Import the scraping function

# Directory to store tweet files
DATA_DIR = "tweets_data"
KEYWORDS_FILE = "keywords.json"

def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_keywords(keywords):
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(keywords, f, indent=4, ensure_ascii=False)

def load_tweets(keyword):
    filename = os.path.join(DATA_DIR, f"{keyword}.json")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def main():
    st.title("🔍 Nitter Tweet Viewer")

    # Load keywords
    keywords = load_keywords()

    # Sidebar for managing keywords
    st.sidebar.header("⚙ Manage Keywords")
    new_keyword = st.sidebar.text_input("Enter new keyword:")

    if st.sidebar.button("➕ Add & Scrape Keyword"):
        if new_keyword and new_keyword not in keywords:
            keywords.append(new_keyword)
            save_keywords(keywords)
            st.sidebar.success(f"✅ Added keyword: {new_keyword}")
            
            # Start scraping immediately
            with st.spinner(f"🔄 Scraping tweets for `{new_keyword}`... Please wait!"):
                scrape_tweets(new_keyword)  # Scrape tweets for the new keyword
                time.sleep(2)  # Give time to store data
            
            st.sidebar.success("✅ Scraping completed! Reload the page to see results.")

        elif new_keyword in keywords:
            st.sidebar.warning("⚠ Keyword already exists. No need to scrape again.")
        else:
            st.sidebar.error("❌ Enter a valid keyword.")

    # Select a keyword to view tweets
    selected_keyword = st.sidebar.selectbox("📌 Select a keyword", keywords)

    if selected_keyword:
        st.subheader(f"📌 Showing results for: `{selected_keyword}`")

        # Load and display stored tweets
        stored_tweets = load_tweets(selected_keyword)

        if stored_tweets:
            for tweet in stored_tweets:
                st.markdown(f"**{tweet['full_name']} (@{tweet['username']})**")
                st.write(tweet["content"])
                st.write(f"🕒 {tweet['date']} | 💬 {tweet['comments']} | 🔄 {tweet['retweets']} | 💬 {tweet['quotes']} | ❤️ {tweet['likes']}")
                st.markdown(f"[🔗 View Tweet]({tweet['tweet_link']})")
                if tweet["images"]:
                    for img in tweet["images"]:
                        st.image(img, use_column_width=True)
                st.markdown("---")
        else:
            st.warning("No tweets found. Try reloading the page or adding a new keyword.")

if __name__ == "__main__":
    main()
