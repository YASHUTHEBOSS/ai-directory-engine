import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Load local .env file if present; safely ignored on GitHub Actions
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")  # Matches your GitHub Secret name exactly

# 2. Initialize the Supabase Client (Admin Mode)
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing Supabase keys. Check your environment configuration.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_new_tools():
    """
    Simulating the agent discovering two new video tools and extracting structured data.
    """
    print("🔍 Agent scanning for new AI Video Tools...")
    
    discovered_tools = [
        {
            "tool_name": "Invideo AI",
            "slug": "invideo-ai",
            "category": "Video Generation",
            "logo_url": "https://invideo.io/favicon.ico",
            "website_url": "https://invideo.io",
            "affiliate_url": "https://invideo.io/?ref=your_affiliate_id",
            "has_free_tier": True,
            "starting_price_usd": 20.00,
            "max_video_length_seconds": 900,
            "forces_watermark": True,
            "bluf_summary": "Invideo AI generates highly engaging faceless YouTube Shorts with stock footage, but forces a prominent watermark on the free tier."
        },
        {
            "tool_name": "ElevenLabs",
            "slug": "elevenlabs",
            "category": "AI Voice Generation",
            "logo_url": "https://elevenlabs.io/favicon.ico",
            "website_url": "https://elevenlabs.io",
            "affiliate_url": "https://elevenlabs.io/?ref=your_affiliate_id",
            "has_free_tier": True,
            "starting_price_usd": 5.00,
            "max_video_length_seconds": 600,
            "forces_watermark": False,
            "bluf_summary": "ElevenLabs provides the most realistic AI voice cloning for video creators. The $5 tier is mandatory for commercial YouTube rights."
        }
    ]
    
    return discovered_tools

def update_database(tools):
    """
    Takes discovered tools and upserts them into Supabase.
    """
    print(f"📥 Attempting to insert {len(tools)} tools into Supabase...")
    
    try:
        response = supabase.table("ai_tools").upsert(tools).execute()
        print("✅ Success! The database has been updated.")
        print(f"📊 Rows affected: {len(response.data)}")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")

# 3. Run the Agent
if __name__ == "__main__":
    new_tools = scrape_new_tools()
    update_database(new_tools)
