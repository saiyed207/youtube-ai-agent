import os
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI

# 1. Load your hidden secrets
YT_API_KEY = os.environ['YT_API_KEY']
HF_TOKEN = os.environ['HF_TOKEN']
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

if 'items' not in response or not response['items']:
    print("No new videos found in the last 24 hours. Exiting.")
    exit()

video_text = ""
for item in response.get("items", []):
    title = item["snippet"]["title"]
    video_id = item["id"]["videoId"]
    video_text += f"Title: {title}\nLink: https://www.youtube.com/watch?v={video_id}\n\n"

# 3. Sending data to AI Agent using EXACTLY your provided code
print("Sending data to AI Agent...")

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

prompt_message = f"You are an expert developer. Read these YouTube video titles. Filter out clickbait and write a friendly email summarizing the best ones I should watch today. Include the YouTube links:\n\n{video_text}"

completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1:novita",
    messages=[
        {
            "role": "user",
            "content": prompt_message
        }
    ],
)

# Extracting the text from your exact completion format
ai_response_text = completion.choices[0].message.content

# 4. Email the final newsletter to yourself
print("Sending email...")
msg = MIMEMultipart()
msg['From'] = EMAIL_ADDRESS
msg['To'] = EMAIL_ADDRESS
msg['Subject'] = "🚀 Your DeepSeek AI Agent Report"

msg.attach(MIMEText(ai_response_text, 'plain'))

# Connect to Gmail and send
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
server.send_message(msg)
server.quit()

print("Success! Email delivered.")
