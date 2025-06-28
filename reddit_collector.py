import praw
import config
from pyairtable import Table
import google.generativeai as genai
import time
import json

# --- UPGRADED MODEL AND CONFIGURATION ---
genai.configure(api_key=config.GEMINI_API_KEY)
# We are now using the superior model you discovered, with a higher rate limit.
model = genai.GenerativeModel('gemini-2.0-flash-lite')
# ----------------------------------------

def extract_product_name(title):
    print(f"      > Asking AI to extract product name from: '{title[:60]}...'")
    try:
        prompt = f"""
        From the following social media post title, extract only the most likely product name.
        Your response must be ONLY the product name and nothing else.
        If it's a brand and a product, include both. For example, for "My new Analogue N64 is here!", you should respond "Analogue N64".
        If there is no clear product, respond with "N/A".

        Title: "{title}"
        """
        response = model.generate_content(prompt)
        product_name = response.text.strip().replace('"', '')
        if product_name.lower() == 'n/a':
            return None
        return product_name
    except Exception as e:
        print(f"        - AI extraction failed: {e}")
        return None

def run():
    print("Starting Reddit Collector...")
    try:
        table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.SOURCE_TABLE_NAME)
        existing_records = table.all(fields=['SourceURL'])
        existing_urls = {record['fields'].get('SourceURL') for record in existing_records}

        reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT,
        )

        new_mentions_found = 0
        for subreddit_name in config.SUBREDDITS:
            print(f"  > Scanning top weekly posts in r/{subreddit_name}...")
            subreddit = reddit.subreddit(subreddit_name)

            for post in subreddit.top(time_filter='week', limit=config.POST_LIMIT):
                if not post.is_self and post.url not in existing_urls:
                    clean_product_name = extract_product_name(post.title)

                    # --- FASTER, SAFER THROTTLE ---
                    # 3 seconds is safe for our new 30 RPM limit (20 RPM effective rate).
                    time.sleep(3)
                    # ----------------------------

                    if not clean_product_name:
                        print("        - AI deemed title not product-related. Skipping.")
                        continue

                    record = {
                        "ProductName": clean_product_name, "SourcePlatform": "Reddit",
                        "PostTitle": post.title, "SourceURL": post.url, "Upvotes": post.score
                    }
                    table.create(record)
                    existing_urls.add(post.url)
                    new_mentions_found += 1
                    print(f"    - Found new top post. Product: '{clean_product_name}'")

        print(f"Reddit Collector finished. Found {new_mentions_found} new weekly top mentions.")
        return new_mentions_found
    except Exception as e:
        print(f"An error occurred in Reddit Collector: {e}")
        return 0