from flask import Flask, jsonify
import config
import reddit_collector
import trends_collector
import master_analyzer

app = Flask(__name__)

if not all([config.GEMINI_API_KEY, config.AIRTABLE_API_KEY, config.REDDIT_CLIENT_ID]):
    print("FATAL ERROR: A critical API key is missing. Please check your Replit Secrets.")

@app.route('/')
def home():
    """Simple homepage to confirm the server is running."""
    return "<h1>E-Com Vault TrendSpotter API</h1><p>The server is running. Append /run-full-pipeline to the URL to execute the trend analysis workflow.</p>"

@app.route('/run-full-pipeline')
def run_pipeline():
    """This endpoint triggers the entire three-step pipeline."""
    print("\n\n===== STARTING FULL PIPELINE RUN =====")

    new_mentions = reddit_collector.run()
    validated_count = trends_collector.run()
    analyzed_count = master_analyzer.run()

    print("===== PIPELINE RUN COMPLETED =====\n\n")

    return jsonify({
        "status": "success",
        "pipeline_summary": {
            "1_discovery_reddit": f"Found {new_mentions} new product mentions.",
            "2_validation_google_trends": f"Processed {validated_count} products for trend data.",
            "3_analysis_gemini": f"Generated new AI analysis for {analyzed_count} products."
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)