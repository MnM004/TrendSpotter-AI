import os

# API Keys loaded securely from Replit Secrets
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')

# Airtable Configuration for our Single Base setup
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
SOURCE_TABLE_NAME = 'All Sources'
GOOGLE_TABLE_NAME = 'Validation: Google Trends'
MASTER_TABLE_NAME = 'Master Analysis'

# --- NEW EXPANDED REDDIT CONFIGURATION ---
SUBREDDITS = [
    'HelpMeFindThis',
    'BuyItForLife',
    'ifyoulikeblank',
    'GoodValue',
    'dealsonamazon',
    'interestingasfuck',
    'DidntKnowIWantedThat',
    'gadgets',
    'ofcoursethatsathing',
    'shutupandtakemymoney', 
    'INEEEEDIT',
]
POST_LIMIT = 10 # Top 10 posts PER WEEK
# ----------------------------------------