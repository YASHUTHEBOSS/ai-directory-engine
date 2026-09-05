import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Setup Database Connection
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing Supabase keys. Check your environment configuration.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_live_tools():
    print("🔍 Crawling the web for live AI tools...")
    
    # Target: A public, anti-bot-free AI directory to ensure consistent daily scraping
    url = "https://github.com/steven2358/awesome-generative-ai"
    
    # Fetch the raw HTML content
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to fetch webpage. Status: {response.status_code}")
        return []
        
    # Parse the HTML tree
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Locate the main content body
    article = soup.find("article", class_="markdown-body")
    if not article:
        return []

    discovered_tools = []
    
    # Extract data by finding all list items <li> containing anchor tags <a>
    for li in article.find_all("li"):
        link = li.find("a")
        
        # Verify it is an external link
        if link and link.get("href", "").startswith("http"):
            tool_name = link.text.strip()
            website_url = link["href"]
            
            # The summary is the remaining text after the link
            full_text = li.text.strip()
            description = full_text.replace(tool_name, "", 1).strip(" -:—")
            
            # Filter for valid, substantial entries
            if 2 < len(tool_name) < 30 and len(description) > 15:
                # Generate a clean URL slug (e.g., "Chat GPT" -> "chat-gpt")
                slug = re.sub(r'[^a-z0-9]+', '-', tool_name.lower()).strip('-')
                
                discovered_tools.append({
                    "tool_name": tool_name,
                    "slug": slug,
                    "category": "Generative AI",
                    "website_url": website_url,
                    "has_free_tier": True,
                    "bluf_summary": description[:200] + "..." if len(description) > 200 else description
                })
                
                # Limit to 6 new tools per run to protect free database limits
                if len(discovered_tools) >= 6:
                    break
                    
    return discovered_tools

def update_database(tools):
    if not tools:
        print("No tools found.")
        return
        
    print(f"📥 Attempting to insert {len(tools)} live tools into Supabase...")
    try:
        response = supabase.table("ai_tools").upsert(tools).execute()
        print(f"✅ Success! {len(tools)} real tools added to your live directory.")
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    new_tools = scrape_live_tools()
    update_database(new_tools)
