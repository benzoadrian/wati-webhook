from fastapi import FastAPI, Request
import openai
import os
import requests
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# API Keys (Loaded from .env)
openai.api_key = os.getenv("OPENAI_API_KEY")
WATI_API_KEY = os.getenv("WATI_API_KEY")
WATI_BASE_URL = os.getenv("WATI_BASE_URL")

@app.post("/webhook")
async def wati_webhook(request: Request):
    data = await request.json()
    sender_phone = data.get("waId")  # WhatsApp number
    user_message = data.get("text")  # Message from user

    if not sender_phone or not user_message:
        return {"error": "Invalid payload"}

    # Set assistant behavior dynamically
    system_message = (
        "Vous êtes une secrétaire virtuelle pour une clinique de dermatologie à Paris. "
        "Répondez en français par défaut, sauf si l'utilisateur écrit en anglais."
    )

    # Send message to ChatGPT
    chat_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    reply_text = chat_response["choices"][0]["message"]["content"]

    # Send reply back to user via Wati
    headers = {"Authorization": f"Bearer {WATI_API_KEY}", "Content-Type": "application/json"}
    payload = {"phone": sender_phone, "message": reply_text}
    requests.post(WATI_BASE_URL, json=payload, headers=headers)

    return {"status": "success", "reply": reply_text}
