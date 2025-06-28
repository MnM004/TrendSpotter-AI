import time
from pytrends.request import TrendReq
import pandas as pd
import config
from pyairtable import Table # <-- Importing from the correct new library

def run():
    print("Starting Google Trends Collector...")
    try:
        pytrends = TrendReq(hl='en-US', tz=360)

        # CORRECTED: Create direct connections using the new library's syntax
        source_table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.SOURCE_TABLE_NAME)
        google_table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.GOOGLE_TABLE_NAME)

        # CORRECTED: The method is .all()
        checked_products_records = google_table.all(fields=['ProductName'])
        checked_products = {rec['fields'].get('ProductName', '').lower() for rec in checked_products_records}

        all_ideas = source_table.all(fields=['ProductName'])

        unique_products_to_check = {
            idea['fields'].get('ProductName') for idea in all_ideas 
            if idea['fields'].get('ProductName') and idea['fields'].get('ProductName').lower() not in checked_products
        }

        print(f"Found {len(unique_products_to_check)} new products to check.")
        validated_products = 0

        for product in unique_products_to_check:
            print(f"  > Checking Google Trend for: '{product[:50]}...'")
            try:
                pytrends.build_payload([product], cat=0, timeframe='today 3-m', geo='', gprop='')
                df = pytrends.interest_over_time()
                if not df.empty and product in df.columns:
                    last_value = df[product].iloc[-1]
                    average = df[product].mean()
                    direction = "Stable"
                    if last_value > average * 1.5: direction = "Upward"
                    elif last_value < average * 0.7: direction = "Downward"
                    # CORRECTED: The method is .create()
                    google_table.create({"ProductName": product, "TrendValue": int(last_value), "TrendDirection": direction})
                    validated_products += 1
                else:
                    google_table.create({"ProductName": product, "TrendValue": 0, "TrendDirection": "Stable"})
                time.sleep(2)
            except Exception:
                google_table.create({"ProductName": product, "TrendValue": 0, "TrendDirection": "Stable"})

        print(f"Google Trends Collector finished. Validated {validated_products} products.")
        return validated_products
    except Exception as e:
        print(f"An error occurred in Google Trends Collector: {e}")
        return 0