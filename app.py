import json
import os
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify
from telegram import scrape_tweets  # Import the scraping function

# Directory to store tweet files
DATA_DIR = "tweets_data"
KEYWORDS_FILE = "keywords.json"

app = Flask(__name__)

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

@app.route('/')
def index():
    # Load keywords
    keywords = load_keywords()

    return render_template('index.html', keywords=keywords)

@app.route('/add_keyword', methods=['POST'])
def add_keyword():
    new_keyword = request.form['new_keyword']
    keywords = load_keywords()

    if new_keyword and new_keyword not in keywords:
        keywords.append(new_keyword)
        save_keywords(keywords)

        # Start scraping immediately
        scrape_tweets(new_keyword)
        time.sleep(2)  # Give time to store data

        return redirect(url_for('index'))

    elif new_keyword in keywords:
        return render_template('index.html', keywords=keywords, message="Keyword already exists.")
    else:
        return render_template('index.html', keywords=keywords, message="Please enter a valid keyword.")

@app.route('/view_tweets/<keyword>')
def view_tweets(keyword):
    stored_tweets = load_tweets(keyword)
    return render_template('view_tweets.html', keyword=keyword, tweets=stored_tweets)

if __name__ == '__main__':
    app.run(debug=True)
