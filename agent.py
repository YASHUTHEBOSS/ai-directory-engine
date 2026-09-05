import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
EMAIL_ADDRESS = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_daily_report():
    print("Gathering daily intelligence...")
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()

    # 1. Get New Tools
    tools_response = supabase.table("ai_tools").select("tool_name").gte("created_at", yesterday).execute()
    new_tools = tools_response.data
    
    # 2. Get Visitor Count
    visits_response = supabase.table("site_visits").select("id", count="exact").gte("created_at", yesterday).execute()
    daily_visits = visits_response.count if visits_response.count else 0

    # 3. Format Email
    subject = f"⚡ AI Directory Daily Report: {daily_visits} Visits"
    body = f"Good evening,\n\nHere is your daily directory report.\n\n"
    body += f"👥 Total Visitors Today: {daily_visits}\n\n"
    
    if len(new_tools) > 0:
        body += f"🔧 {len(new_tools)} New Tools Added:\n"
        for tool in new_tools:
            body += f"- {tool['tool_name']}\n"
    else:
        body += "🔧 No new tools discovered today.\n"

    body += "\nSystem running optimally."
    return subject, body

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Standard Gmail SMTP configuration
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ Daily report dispatched successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    subject, body = generate_daily_report()
    send_email(subject, body)
