# trends_collector.py

import time
from pytrends.request import TrendReq
import pandas as pd
import config
from pyairtable import Table

def run():
    print("Starting Google Trends Collector...")
    try:
        pytrends = TrendReq(hl='en-US', tz=360)

        source_table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.SOURCE_TABLE_NAME)
        google_table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.GOOGLE_TABLE_NAME)

        checked_products_records = google_table.all(fields=['ProductName'])
        checked_products = {rec['fields'].get('ProductName', '').lower() for rec in checked_products_records}

        all_ideas = source_table.all(fields=['ProductName'])

        # Use a dictionary to store both the product name and its original record ID
        unique_products_to_check = {}
        for idea in all_ideas:
            if 'ProductName' in idea['fields']:
                product_name = idea['fields']['ProductName']
                if product_name and product_name.lower() not in checked_products:
                    # Key: product name, Value: the ID from the 'All Sources' table
                    unique_products_to_check[product_name] = idea['id']

        print(f"Found {len(unique_products_to_check)} new products to check.")
        validated_products = 0

        # Loop through the dictionary, unpacking both the name and the ID
        for product, source_record_id in unique_products_to_check.items():
            print(f"  > Checking Google Trend for: '{product[:50]}...'")
            try:
                pytrends.build_payload([product], cat=0, timeframe='today 3-m', geo='', gprop='')
                df = pytrends.interest_over_time()
                time.sleep(5) # Throttle after the request

                if not df.empty and product in df.columns:
                    last_value = df[product].iloc[-1]
                    average = df[product].mean()
                    direction = "Stable"
                    if last_value > average * 1.5: direction = "Upward"
                    elif last_value < average * 0.7: direction = "Downward"

                    # Create the record WITH the Source Link
                    google_table.create({
                        "ProductName": product, 
                        "TrendValue": int(last_value), 
                        "TrendDirection": direction,
                        "Source Link": [source_record_id]  # <-- The crucial fix
                    })
                    validated_products += 1
                else:
                    # Also create a record if trend is empty, so we don't re-check it
                    google_table.create({
                        "ProductName": product, 
                        "TrendValue": 0, 
                        "TrendDirection": "Stable",
                        "Source Link": [source_record_id]
                    })
            except Exception as e:
                print(f"    - Trend check failed for '{product}': {e}. Creating stable record.")
                google_table.create({
                    "ProductName": product, 
                    "TrendValue": 0, 
                    "TrendDirection": "Stable",
                    "Source Link": [source_record_id]
                })

        print(f"Google Trends Collector finished. Validated {validated_products} products.")
        return validated_products
    except Exception as e:
        print(f"An error occurred in Google Trends Collector: {e}")
        return 0

# Add this to allow running the file directly
if __name__ == '__main__':
    run()