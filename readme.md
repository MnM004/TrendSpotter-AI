# TrendSpotter: AI-Powered Product Discovery Pipeline

An automated Python application that discovers, validates, and analyzes trending e-commerce products.

---

## 1. Overview

TrendSpotter is a fully-automated application designed to give e-commerce entrepreneurs an edge by identifying high-potential products before they become saturated. It operates on a robust three-stage data pipeline:

1.  **Discover:** The application scans multiple high-activity subreddits for their top weekly posts. It then uses a powerful Large Language Model (Llama 3 via Groq) to intelligently extract clean product names from messy, conversational post titles.
2.  **Validate:** Each discovered product is validated against Google Trends data to verify that there is genuine and increasing public search interest, filtering out noise and confirming real-world traction.
3.  **Analyze:** For products confirmed to be trending upwards, the LLM performs a deep analysis, generating a concise product summary, a target audience profile, a compelling marketing angle for social media, and a viability score.

All processed data is organized and stored in a structured Airtable database, which serves as a powerful and interactive dashboard for the results.

---

## 2. Architecture & Technologies

- **Backend:** Flask
- **Data Pipeline:** Python scripts
- **AI / LLM:** Groq API with Llama 3 (`llama3-70b-8192`)
- **Data Sources:** Reddit API (`PRAW`), Google Trends (`pytrends`)
- **Database & Dashboard:** Airtable
- **Key Libraries:** `pyairtable`, `openai`, `praw`, `pytrends`

---

## 3. Project Setup

Follow these steps to set up and run the project.

### A. Clone the Repository
Clone this repository to your local machine or a cloud environment like Replit.

### B. Install Dependencies
Install all required Python libraries using the `requirements.txt` file.
```bash
pip install -r requirements.txt
Use code with caution.
Markdown
C. Configure the Airtable Base
Create a single new Airtable base and name it TrendSpotter Pipeline.
Inside this base, create three tables with the exact field names and types specified below:
Table: All Sources
ProductName (Single line text, Primary Field)
SourcePlatform (Single select: "Reddit", "TikTok", "Instagram")
SourceURL (URL)
PostTitle (Long text)
Upvotes (Number)
Table: Validation: Google Trends
ProductName (Single line text, Primary Field)
TrendValue (Number)
TrendDirection (Single select: "Upward", "Stable", "Downward")
Table: Master Analysis
AnalysisID (Autonumber, Primary Field)
Source Link (Link to another record -> All Sources)
ProductName (Formula -> IF({Source Link}, {Source Link}, ''))
Google Trend Link (Link to another record -> Validation: Google Trends)
DataSource (Single select: "Reddit", "TikTok", "Instagram")
ProductSummary (Long text)
TargetAudience (Long text)
MarketingAngle (Long text)
ConfidenceScore (Rating)
SourceURL (URL)
D. Set Up Environment Variables (Secrets)
This project requires API keys to function. In Replit, use the "Secrets" tab.
Variable	Description
AIRTABLE_API_KEY	Your Airtable Personal Access Token.
AIRTABLE_BASE_ID	The ID of your TrendSpotter Pipeline base.
GROQ_API_KEY	Your API key from GroqCloud.
REDDIT_CLIENT_ID	Your Reddit App Client ID.
REDDIT_CLIENT_SECRET	Your Reddit App Client Secret.
REDDIT_USER_AGENT	A descriptive user agent (e.g., TrendSpotter v1).
4. How to Run
Run the Flask Server:
Generated bash
python main.py
Use code with caution.
Bash
Trigger the Pipeline: Once the server is running, navigate to the following URL in your browser to execute the full data pipeline:
Generated code
http://127.0.0.1:8080/run-full-pipeline
Use code with caution.
Monitor: Watch the console output for real-time progress. The results will appear in your Airtable base as the pipeline completes.