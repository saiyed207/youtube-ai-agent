import os
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai

# 1. Load your hidden secrets
YT_API_KEY = os.environ['YT_API_KEY']
GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

# 2. Ask YouTube for the top coding videos from the last 24 hours
yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat("T") + "Z"
url = "https://youtube.googleapis.com/youtube/v3/search"
params = {
    "part": "snippet",
    "q": "coding | programming | web development | python | AI",
    "order": "viewCount",
    "publishedAfter": yesterday,
    "maxResults": 5,
    "type": "video",
    "key": YT_API_KEY
}

print("Fetching videos from YouTube...")
response = requests.get(url, params=params).json()

video_text = ""
for item in response.get("items", []):
    title = item["snippet"]["title"]
    desc = item["snippet"]["description"]
    video_id = item["id"]["videoId"]
    video_text += f"Title: {title}\nLink: https://www.youtube.com/watch?v={video_id}\nDescription: {desc}\n\n"

# 3. Send the videos to the AI Agent to evaluate
print("Sending data to AI Agent...")
genai.configure(api_key=GEMINI_API_KEY)

# Using the exact model you requested for speed and efficiency
model = genai.GenerativeModel('gemini-1.5-flash-latest') 

prompt = f"""
You are an expert developer and tech analyst. I have found the most-viewed coding and AI videos on YouTube from the last 24 hours. 
Read their titles and descriptions below. Filter out any clickbait or low-quality content. 
Write a friendly, highly readable email newsletter summarizing the 2-3 absolute best and most valuable videos I should watch today.
For each video, explain WHY it is worth watching in a single sentence.
Make sure to include the YouTube links for each video you recommend.

Here is the data:
{video_text}
"""

ai_response = model.generate_content(prompt).text

# 4. Email the final newsletter to yourself
print("Sending email...")
msg = MIMEMultipart()
msg['From'] = EMAIL_ADDRESS
msg['To'] = EMAIL_ADDRESS 
msg['Subject'] = "⚡️ Your AI Agent's Daily Flash Briefing"

msg.attach(MIMEText(ai_response, 'plain'))

# Connect to Gmail and send
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
server.send_message(msg)
server.quit()

print("Success! Email delivered.")
