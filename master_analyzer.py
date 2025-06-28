import google.generativeai as genai
import config
import json
from pyairtable import Table

def run():
    print("Starting Master Analyzer...")
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        # THIS IS THE CORRECTED MODEL NAME
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

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
            product_name = trend_record['fields']['ProductName']
            google_trend_record_id = trend_record['id']
            print(f"  > Analyzing with Gemini: {product_name[:50]}...")

            sanitized_name = product_name.replace("'", "\\'")
            formula = f"{{ProductName}} = '{sanitized_name}'"
            source_records = source_table.all(formula=formula, max_records=1)

            if not source_records: continue

            source_record = source_records[0]
            source_record_id = source_record['id']
            source_platform = source_record['fields'].get('SourcePlatform')
            source_url = source_record['fields'].get('SourceURL')

            prompt = f"""You are an expert E-commerce Product Analyst for a company called E-com Vault. Your job is to find winning products for dropshippers who use a sales funnel strategy. Analyze the following product data and return your analysis ONLY in a valid JSON format. Do not add any text before or after the JSON object. Data: - Product Name: "{product_name}" - Source Platform: "{source_platform}" - Google Trend Direction: "Upward". Required JSON Output: {{"product_summary": "A concise, one-sentence description of what this product is and who it's for.", "target_audience": "Describe the ideal customer for this product. Be specific about demographics, pain points, and interests.", "marketing_angle": "Suggest a powerful hook for a 15-second video ad. Focus on a strong emotion, problem-solving aspect, or a 'wow' factor.", "confidence_score": "Provide an integer score from 1 to 5 representing your confidence in this product's potential for a sales funnel. 1 is low, 5 is high."}}"""
            try:
                response = model.generate_content(prompt)
                cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
                analysis_data = json.loads(cleaned_response)

                master_table.create({
                    "Source Link": [source_record_id], "Google Trend Link": [google_trend_record_id],
                    "DataSource": source_platform, "ProductSummary": analysis_data.get("product_summary"),
                    "TargetAudience": analysis_data.get("target_audience"), "MarketingAngle": analysis_data.get("marketing_angle"),
                    "ConfidenceScore": analysis_data.get("confidence_score"), "SourceURL": source_url
                })
                products_analyzed += 1
            except Exception as e:
                print(f"    - Gemini analysis failed for '{product_name}': {e}")

        print(f"Master Analyzer finished. Analyzed {products_analyzed} new products.")
        return products_analyzed
    except Exception as e:
        print(f"An error occurred in Master Analyzer: {e}")
        return 0