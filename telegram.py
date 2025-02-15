import time
import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Directory to store tweets
DATA_DIR = "tweets_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

KEYWORDS_FILE = "keywords.json"

# Webhook & Bot Credentials
TELEGRAM_BOT_TOKEN = "7245489755:AAFxaw-XmOmiIYkn4cVrEWcCXCk1gybYhD4"
TELEGRAM_CHAT_ID = "577964024"  # Replace with your chat ID

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_tweets(keyword):
    filename = os.path.join(DATA_DIR, f"{keyword}.json")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tweets(keyword, tweets):
    filename = os.path.join(DATA_DIR, f"{keyword}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(tweets, f, indent=4, ensure_ascii=False)



def send_to_telegram(tweet):
    """Send new tweets to Telegram."""
    text = f"**{tweet['full_name']} (@{tweet['username']})**\n"
    text += f"{tweet['content']}\n\n"
    text += f"🕒 {tweet['date']} | 💬 {tweet['comments']} | 🔄 {tweet['retweets']} | 💬 {tweet['quotes']} | ❤️ {tweet['likes']}\n"
    text += f"[🔗 View Tweet]({tweet['tweet_link']})"

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}

    response = requests.post(telegram_url, json=payload)
    if response.status_code == 200:
        print(f"[INFO] Sent to Telegram: {tweet['tweet_link']}")
    else:
        print(f"[ERROR] Telegram failed: {response.status_code}")

def scrape_tweets(keyword, max_scrolls=3):
    search_query = "+".join(keyword.split())
    url = f"https://nitter.net/search?f=tweets&q={search_query}"

    driver = init_driver()
    driver.get(url)
    time.sleep(5)

    existing_tweets = load_tweets(keyword)
    existing_ids = {tweet["tweet_id"] for tweet in existing_tweets}
    new_tweets = []

    for _ in range(max_scrolls):
        tweet_elements = driver.find_elements(By.CLASS_NAME, "timeline-item")

        for item in tweet_elements:
            try:
                username = item.find_element(By.CLASS_NAME, "username").text.strip()
                full_name = item.find_element(By.CLASS_NAME, "fullname").text.strip()
                tweet_content = item.find_element(By.CLASS_NAME, "tweet-content").text.strip()
                tweet_date = item.find_element(By.CLASS_NAME, "tweet-date").text.strip()
                tweet_link = item.find_element(By.CLASS_NAME, "tweet-link").get_attribute("href")
                tweet_id = tweet_link.split("/")[-1]

                if tweet_id in existing_ids:
                    continue  # Skip if already saved

                stats = item.find_elements(By.CLASS_NAME, "tweet-stat")
                comments = stats[0].text.strip() if len(stats) > 0 else "0"
                retweets = stats[1].text.strip() if len(stats) > 1 else "0"
                quotes = stats[2].text.strip() if len(stats) > 2 else "0"
                likes = stats[3].text.strip() if len(stats) > 3 else "0"

                images = [img.get_attribute("href") for img in item.find_elements(By.CLASS_NAME, "still-image")]

                tweet_data = {
                    "tweet_id": tweet_id,
                    "full_name": full_name,
                    "username": username,
                    "content": tweet_content,
                    "date": tweet_date,
                    "tweet_link": tweet_link,
                    "comments": comments,
                    "retweets": retweets,
                    "quotes": quotes,
                    "likes": likes,
                    "images": images,
                }

                new_tweets.append(tweet_data)
                # send_to_discord(tweet_data)  # Send to Discord
                send_to_telegram(tweet_data)  # Send to Telegram

            except Exception as e:
                print(f"[ERROR] Failed to extract tweet: {e}")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    driver.quit()

    if new_tweets:
        all_tweets = new_tweets + existing_tweets
        save_tweets(keyword, all_tweets)
        print(f"[INFO] {len(new_tweets)} new tweets added for '{keyword}'.")

def main():
    keywords = load_keywords()
    if not keywords:
        print("[ERROR] No keywords found in 'keywords.json'.")
        return

    print("[INFO] Starting tweet scraping...")
    for keyword in keywords:
        print(f"[INFO] Scraping tweets for '{keyword}'...")
        scrape_tweets(keyword)

if __name__ == "__main__":
    main()
