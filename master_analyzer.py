# In master_analyzer.py

# (Your imports should already include Groq, Table, config, json)
from groq import Groq
from pyairtable import Table
import config
import json

# --- GROQ CLIENT SETUP ---
client = Groq(api_key=config.GROQ_API_KEY)

def run():
    print("Starting Master Analyzer...")
    try:
        master_table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.MASTER_TABLE_NAME)
        google_table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.GOOGLE_TABLE_NAME)
        source_table = Table(config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.SOURCE_TABLE_NAME)

        analyzed_records = master_table.all(fields=['Google Trend Link'])
        analyzed_trend_ids = {rec['fields'].get('Google Trend Link', [None])[0] for rec in analyzed_records if 'Google Trend Link' in rec['fields']}
        upward_trends = google_table.all(formula="{TrendDirection} = 'Upward'")
        products_to_analyze = [trend for trend in upward_trends if trend['id'] not in analyzed_trend_ids]

        print(f"Found {len(products_to_analyze)} upward-trending products to analyze.")
        products_analyzed = 0

        for trend_record in products_to_analyze:
            if 'Source Link' not in trend_record['fields']:
                print(f"  > Skipping trend record {trend_record['id']} because 'Source Link' is missing.")
                continue

            # --- NEW: GATHER MORE DATA FOR THE PROMPT ---
            source_record_id = trend_record['fields']['Source Link'][0]
            source_record = source_table.get(source_record_id)

            product_name = source_record['fields'].get('ProductName')
            source_platform = source_record['fields'].get('SourcePlatform')
            source_url = source_record['fields'].get('SourceURL')
            upvotes = source_record['fields'].get('Upvotes', 0) # Get upvotes, default to 0 if missing

            google_trend_record_id = trend_record['id']
            trend_value = trend_record['fields'].get('TrendValue', 0) # Get the numerical trend value
            # --- END NEW DATA GATHERING ---

            print(f"  > Analyzing with Groq (Llama3-70b): {product_name[:50]}...")

            # --- UPDATED PROMPT ---
            prompt = f"""
            You are an expert E-commerce Product Analyst. Analyze the following data to determine a product's potential for a sales funnel.
            Your analysis MUST be returned ONLY in a valid JSON format.

            Data:
            - Product Name: "{product_name}"
            - Source Platform: "{source_platform}"
            - Source Upvotes: {upvotes}
            - Google Trend Direction: "Upward"
            - Google Trend Intensity (0-100): {trend_value}

            Instructions for Confidence Score:
            Base your confidence score on the combined strength of the social proof (Upvotes) and the trend data (Trend Intensity).
            A product with high upvotes AND high trend intensity should get a 5. A product with low upvotes or low trend intensity, even if the trend is 'Upward', should get a lower score (2 or 3).

            Required JSON Output:
            {{
                "product_summary": "A concise, one-sentence description of what this product is and who it's for.",
                "target_audience": "Describe the ideal customer for this product. Be specific about demographics, pain points, and interests.",
                "marketing_angle": "Suggest a powerful hook for a 15-second video ad. Focus on a strong emotion, problem-solving aspect, or a 'wow' factor.",
                "confidence_score": "Provide an integer score from 1 to 5 based on the instructions."
            }}
            """
            # --- END UPDATED PROMPT ---

            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                analysis_data = json.loads(chat_completion.choices[0].message.content)

                master_table.create({
                    "Source Link": [source_record_id], "Google Trend Link": [google_trend_record_id],
                    "DataSource": source_platform, "ProductSummary": analysis_data.get("product_summary"),
                    "TargetAudience": analysis_data.get("target_audience"), "MarketingAngle": analysis_data.get("marketing_angle"),
                    "ConfidenceScore": analysis_data.get("confidence_score"), "SourceURL": source_url
                })
                products_analyzed += 1
            except Exception as e:
                print(f"    - Groq analysis failed for '{product_name}': {e}")

        print(f"Master Analyzer finished. Analyzed {products_analyzed} new products.")
        return products_analyzed
    except Exception as e:
        print(f"An error occurred in Master Analyzer: {e}")
        return 0

# Add this to allow running the file directly
if __name__ == '__main__':
    run()